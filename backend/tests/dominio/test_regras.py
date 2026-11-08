import pytest

from app.dominio.entidades import DadosJogo, Jogo, validar_dados_jogo
from app.dominio.erros import Conflito, DadosInvalidos
from app.dominio.regras import (descobrir_extensao_capa, normalizar_email, validar_nota,
                                validar_senha)
from datetime import datetime, timezone


def test_email_e_normalizado():
    assert normalizar_email("  Diego@Mail.COM ") == "diego@mail.com"


@pytest.mark.parametrize("email", ["", "sem-arroba", "a@b", "a b@c.com"])
def test_email_invalido(email):
    with pytest.raises(DadosInvalidos) as erro:
        normalizar_email(email)
    assert erro.value.codigo == "email_invalido"


def test_senha_curta_recusada_e_oito_aceita():
    with pytest.raises(DadosInvalidos):
        validar_senha("1234567")
    assert validar_senha("12345678") == "12345678"


@pytest.mark.parametrize("nota", [0, 6, -1])
def test_nota_fora_de_1_a_5(nota):
    with pytest.raises(DadosInvalidos):
        validar_nota(nota)


def test_capa_reconhece_tipos_e_recusa_outros():
    assert descobrir_extensao_capa(b"\xff\xd8\xff" + b"0" * 10) == "jpg"
    assert descobrir_extensao_capa(b"\x89PNG\r\n\x1a\n" + b"0") == "png"
    assert descobrir_extensao_capa(b"RIFF0000WEBP" + b"0") == "webp"
    with pytest.raises(DadosInvalidos) as erro:
        descobrir_extensao_capa(b"%PDF-1.4")
    assert erro.value.codigo == "capa_tipo"


def test_capa_muito_grande():
    with pytest.raises(DadosInvalidos) as erro:
        descobrir_extensao_capa(b"\xff\xd8\xff" + b"0" * (2 * 1024 * 1024))
    assert erro.value.codigo == "capa_grande"


def test_dados_do_jogo_exigem_console_e_ano_valido():
    with pytest.raises(DadosInvalidos):
        validar_dados_jogo(DadosJogo("Fifa 18", 2017, 1, 1, []))
    with pytest.raises(DadosInvalidos):
        validar_dados_jogo(DadosJogo("Fifa 18", 1800, 1, 1, [1]))
    ok = validar_dados_jogo(DadosJogo("  Fifa 18 ", 2017, 1, 1, [2, 1, 1]))
    assert ok.nome == "Fifa 18" and ok.console_ids == [1, 2]


def test_jogo_exclui_e_restaura():
    jogo = Jogo("Zelda", 1998, 1, 1, [1], cadastrado_por_id=1)
    jogo.excluir(7, datetime.now(timezone.utc))
    assert jogo.excluido and jogo.excluido_por_id == 7
    with pytest.raises(Conflito):
        jogo.excluir(7, datetime.now(timezone.utc))
    jogo.restaurar()
    assert not jogo.excluido and jogo.excluido_por_id is None
    with pytest.raises(Conflito):
        jogo.restaurar()
