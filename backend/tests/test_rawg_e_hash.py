import httpx
import pytest

from app.adaptadores.cliente_externo import FonteIgdb, FonteRawg
from app.adaptadores.hash_senha import HashScrypt
from app.adaptadores.token_jwt import TokenJwt
from app.dominio.erros import FonteExternaIndisponivel


S = "s" * 40


def cliente_falso(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_rawg_converte_a_resposta_em_lancamentos():
    corpo = {"results": [
        {"name": "Jogo A", "released": "2027-03-01", "background_image": "https://media.rawg.io/a.jpg", "platforms": [{"platform": {"name": "PC"}}, {"platform": {"name": "PS5"}}]},
        {"name": "Jogo B", "released": None, "platforms": None}]}
    fonte = FonteRawg("chave", cliente=cliente_falso(lambda req: httpx.Response(200, json=corpo)))
    a, b = fonte.proximos()
    assert (a.nome, str(a.data_lancamento), a.plataformas, a.origem) == ("Jogo A", "2027-03-01", "PC, PS5", "RAWG")
    assert a.capa_url == "https://media.rawg.io/a.jpg"
    assert b.data_lancamento is None and b.plataformas == "" and b.capa_url is None


def test_rawg_fora_do_ar_ou_sem_chave():
    with pytest.raises(FonteExternaIndisponivel):
        FonteRawg("chave", cliente=cliente_falso(lambda req: httpx.Response(500))).proximos()
    with pytest.raises(FonteExternaIndisponivel) as erro:
        FonteRawg("").proximos()
    assert erro.value.codigo == "rawg_sem_chave"


def test_hash_nao_guarda_senha_e_confere():
    h = HashScrypt()
    a, b = h.gerar("senha-forte"), h.gerar("senha-forte")
    assert a != b and "senha-forte" not in a
    assert h.conferir("senha-forte", a) and not h.conferir("outra", a) and not h.conferir("x", "lixo")


def test_token_valido_adulterado_e_expirado():
    t = TokenJwt(S, 60)
    assert t.ler(t.gerar(7)) == 7
    assert t.ler(t.gerar(7) + "x") is None
    assert TokenJwt(S + "x", 60).ler(t.gerar(7)) is None
    assert TokenJwt(S, -1).ler(TokenJwt(S, -1).gerar(7)) is None


def test_igdb_pede_os_mais_aguardados_e_converte():
    chamadas = []

    def tratar(req):
        chamadas.append(req)
        if "oauth2/token" in str(req.url):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 100})
        assert req.headers["Authorization"] == "Bearer tok" and req.headers["Client-ID"] == "id"
        consulta = req.content.decode()
        assert "sort hypes desc" in consulta and "hypes > 0" in consulta and "limit 20" in consulta
        return httpx.Response(200, json=[
            {"id": 2, "name": "Jogo B", "first_release_date": 1900172800, "hypes": 90},
            {"id": 1, "name": "Jogo A", "first_release_date": 1900000000, "hypes": 500,
             "cover": {"id": 5, "image_id": "co1abc"}, "platforms": [{"id": 6, "name": "PC"}, {"id": 48, "name": "PS4"}]},
            {"id": 3, "name": "Sem data", "hypes": 10},
            {"id": 4, "first_release_date": 1900000000},
        ])

    a, b = FonteIgdb("id", "segredo", cliente=cliente_falso(tratar)).proximos()
    assert (a.nome, a.plataformas, a.origem, str(a.data_lancamento)) == ("Jogo A", "PC, PS4", "IGDB", "2030-03-17")
    assert a.capa_url == "https://images.igdb.com/igdb/image/upload/t_cover_big/co1abc.jpg"
    assert (b.nome, b.plataformas, b.capa_url) == ("Jogo B", "", None)  # ordenados por data, não por popularidade
    assert len(chamadas) == 2


def test_igdb_sem_chave_ou_fora_do_ar():
    with pytest.raises(FonteExternaIndisponivel) as erro:
        FonteIgdb("", "").proximos()
    assert erro.value.codigo == "igdb_sem_chave"
    with pytest.raises(FonteExternaIndisponivel) as erro:
        FonteIgdb("id", "x", cliente=cliente_falso(lambda req: httpx.Response(403))).proximos()
    assert erro.value.codigo == "igdb_fora"


def test_limitador_bloqueia_e_libera_com_o_tempo():
    from app.adaptadores.limitador import LimitadorEmMemoria
    agora = [0.0]
    lim = LimitadorEmMemoria(max_falhas=2, janela_segundos=60, relogio=lambda: agora[0])
    lim.registrar_falha("k"); assert not lim.bloqueado("k")
    lim.registrar_falha("k"); assert lim.bloqueado("k") and not lim.bloqueado("outro")
    agora[0] = 61.0
    assert not lim.bloqueado("k")
