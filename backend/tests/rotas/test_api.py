import io

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 30


def cadastrar_e_logar(cliente, email="diego@mail.com", nome="Diego"):
    r = cliente.post("/usuarios", json={"nome": nome, "email": email, "senha": "senha-forte"})
    assert r.status_code == 201
    r = cliente.post("/auth/login", json={"email": email, "senha": "senha-forte"})
    assert r.status_code == 200
    return r


def dados_jogo(**kw):
    d = {"nome": "Fifa 18", "ano": "2017", "genero_id": "4", "faixa_etaria_id": "1", "console_ids": ["1", "8"]}
    d.update(kw)
    return d


def test_cadastro_nao_expoe_a_senha(cliente):
    r = cliente.post("/usuarios", json={"nome": "Diego", "email": "d@mail.com", "senha": "senha-forte"})
    assert r.status_code == 201 and "senha" not in r.text and "hash" not in r.text


def test_cadastro_com_email_repetido_e_senha_curta(cliente):
    cadastrar_e_logar(cliente)
    r = cliente.post("/usuarios", json={"nome": "Xx", "email": "diego@mail.com", "senha": "senha-forte"})
    assert r.status_code == 409 and r.json()["codigo"] == "email_em_uso"
    r = cliente.post("/usuarios", json={"nome": "Xx", "email": "x@mail.com", "senha": "123"})
    assert r.status_code == 422 and r.json()["codigo"] == "senha_curta"


def test_login_poe_cookie_httponly_e_eu_funciona(cliente):
    r = cadastrar_e_logar(cliente)
    assert "httponly" in r.headers["set-cookie"].lower()
    assert cliente.get("/auth/eu").json()["email"] == "diego@mail.com"


def test_login_errado_e_sem_login(cliente):
    cadastrar_e_logar(cliente)
    anonimo = cliente.__class__(cliente.app)
    assert anonimo.post("/auth/login", json={"email": "diego@mail.com", "senha": "errada-123"}).status_code == 401
    for rota in ("/jogos", "/lancamentos", "/auth/eu"):
        assert anonimo.get(rota).status_code == 401


def test_logout_apaga_o_acesso(cliente):
    cadastrar_e_logar(cliente)
    assert cliente.post("/auth/logout").status_code == 204
    assert cliente.get("/auth/eu").status_code == 401


def test_idioma(cliente):
    cadastrar_e_logar(cliente)
    assert cliente.put("/usuarios/eu/idioma", json={"idioma": "en"}).json()["idioma"] == "en"
    assert cliente.put("/usuarios/eu/idioma", json={"idioma": "fr"}).status_code == 422


def test_referencias_ja_vem_preenchidas(cliente):
    r = cliente.get("/referencias").json()
    assert len(r["generos"]) >= 5 and len(r["faixas_etarias"]) == 6 and len(r["consoles"]) >= 10


def test_ciclo_completo_do_jogo(cliente):
    cadastrar_e_logar(cliente)
    r = cliente.post("/jogos", data=dados_jogo(historia="Futebol"), files={"capa": ("c.png", io.BytesIO(PNG), "image/png")})
    assert r.status_code == 201, r.text
    jogo = r.json()
    assert jogo["cadastrado_por"] == "Diego" and len(jogo["consoles"]) == 2 and jogo["capa_url"]
    assert cliente.get(jogo["capa_url"]).content == PNG  # a capa é servida

    assert cliente.post("/jogos", data=dados_jogo()).status_code == 409  # nome repetido

    r = cliente.put(f"/jogos/{jogo['id']}", data=dados_jogo(nome="Fifa 19", ano="2018"))
    assert r.status_code == 200 and r.json()["nome"] == "Fifa 19" and r.json()["alterado_por"] == "Diego"

    assert [j["nome"] for j in cliente.get("/jogos", params={"texto": "fifa"}).json()] == ["Fifa 19"]
    assert cliente.get("/jogos", params={"console_id": 2}).json() == []

    assert cliente.delete(f"/jogos/{jogo['id']}").json()["excluido"] is True
    assert cliente.get("/jogos").json() == []
    assert len(cliente.get("/jogos", params={"incluir_excluidos": True}).json()) == 1
    assert cliente.post(f"/jogos/{jogo['id']}/restaurar").json()["excluido"] is False
    assert len(cliente.get("/jogos").json()) == 1


def test_outro_usuario_pode_editar_e_fica_registrado(cliente):
    cadastrar_e_logar(cliente)
    jogo = cliente.post("/jogos", data=dados_jogo()).json()
    cadastrar_e_logar(cliente, email="ana@mail.com", nome="Ana")
    r = cliente.put(f"/jogos/{jogo['id']}", data=dados_jogo(nome="Fifa 18 Remaster"))
    assert r.json()["cadastrado_por"] == "Diego" and r.json()["alterado_por"] == "Ana"


def test_capa_que_nao_e_imagem_e_recusada(cliente):
    cadastrar_e_logar(cliente)
    r = cliente.post("/jogos", data=dados_jogo(), files={"capa": ("x.png", io.BytesIO(b"%PDF-1.4"), "image/png")})
    assert r.status_code == 422 and r.json()["codigo"] == "capa_tipo"
    assert cliente.get("/jogos").json() == []


def test_avaliacao_e_media(cliente):
    cadastrar_e_logar(cliente)
    jogo = cliente.post("/jogos", data=dados_jogo()).json()
    assert cliente.put(f"/jogos/{jogo['id']}/avaliacao", json={"nota": 4, "comentario": "bom"}).json()["nota_media"] == 4.0
    cadastrar_e_logar(cliente, email="ana@mail.com", nome="Ana")
    r = cliente.put(f"/jogos/{jogo['id']}/avaliacao", json={"nota": 5}).json()
    assert r["nota_media"] == 4.5 and r["total_avaliacoes"] == 2
    assert {a["usuario"] for a in cliente.get(f"/jogos/{jogo['id']}/avaliacoes").json()} == {"Diego", "Ana"}
    assert cliente.put(f"/jogos/{jogo['id']}/avaliacao", json={"nota": 7}).status_code == 422


def test_lancamentos_comecam_vazios(cliente):
    cadastrar_e_logar(cliente)
    assert cliente.get("/lancamentos").json() == []
