import pytest

from app.casos_de_uso.usuarios import (CadastrarUsuario, EscolherIdioma, FazerLogin,
                                       IdentificarUsuario)
from app.dominio.erros import Conflito, DadosInvalidos, NaoAutenticado
from tests.fakes import FakeHash, FakeLimitador, FakeTokens, FakeUsuarios
from app.dominio.erros import LimiteExcedido


@pytest.fixture
def usuarios():
    return FakeUsuarios()


def cadastrar(usuarios, **kw):
    dados = dict(nome="Diego", email="Diego@Mail.com", senha="senha-forte")
    dados.update(kw)
    return CadastrarUsuario(usuarios, FakeHash()).executar(**dados)


def test_cadastra_usuario_guardando_hash_e_email_minusculo(usuarios):
    u = cadastrar(usuarios)
    assert u.id and u.email == "diego@mail.com"
    assert u.senha_hash != "senha-forte"


def test_email_repetido_gera_conflito(usuarios):
    cadastrar(usuarios)
    with pytest.raises(Conflito) as erro:
        cadastrar(usuarios, email="diego@MAIL.com")
    assert erro.value.codigo == "email_em_uso"


def test_senha_curta_nao_cadastra(usuarios):
    with pytest.raises(DadosInvalidos):
        cadastrar(usuarios, senha="123")
    assert usuarios.itens == {}


def test_login_certo_devolve_token(usuarios):
    cadastrar(usuarios)
    usuario, token = FazerLogin(usuarios, FakeHash(), FakeTokens(), FakeLimitador()).executar("diego@mail.com", "senha-forte")
    assert token == f"token-{usuario.id}"


@pytest.mark.parametrize("email,senha", [("diego@mail.com", "errada123"), ("outro@mail.com", "senha-forte")])
def test_login_errado_nao_revela_o_motivo(usuarios, email, senha):
    cadastrar(usuarios)
    with pytest.raises(NaoAutenticado) as erro:
        FazerLogin(usuarios, FakeHash(), FakeTokens(), FakeLimitador()).executar(email, senha)
    assert erro.value.codigo == "credenciais_invalidas"


def test_identificar_usuario_pelo_token(usuarios):
    u = cadastrar(usuarios)
    caso = IdentificarUsuario(usuarios, FakeTokens())
    assert caso.executar(f"token-{u.id}").id == u.id
    for ruim in (None, "lixo", "token-99"):
        with pytest.raises(NaoAutenticado):
            caso.executar(ruim)


def test_escolher_idioma(usuarios):
    u = cadastrar(usuarios)
    assert EscolherIdioma(usuarios).executar(u.id, "en").idioma == "en"
    with pytest.raises(DadosInvalidos):
        EscolherIdioma(usuarios).executar(u.id, "fr")


def test_login_bloqueia_apos_varias_falhas_ate_com_a_senha_certa(usuarios):
    cadastrar(usuarios)
    caso = FazerLogin(usuarios, FakeHash(), FakeTokens(), FakeLimitador(max_falhas=3))
    for _ in range(3):
        with pytest.raises(NaoAutenticado):
            caso.executar("diego@mail.com", "errada-123", "1.2.3.4")
    with pytest.raises(LimiteExcedido) as erro:
        caso.executar("diego@mail.com", "senha-forte", "1.2.3.4")
    assert erro.value.codigo == "muitas_tentativas"
    assert caso.executar("diego@mail.com", "senha-forte", "9.9.9.9")  # outro IP não é afetado


def test_login_bem_sucedido_zera_as_falhas(usuarios):
    cadastrar(usuarios)
    caso = FazerLogin(usuarios, FakeHash(), FakeTokens(), FakeLimitador(max_falhas=3))
    for _ in range(2):
        with pytest.raises(NaoAutenticado):
            caso.executar("diego@mail.com", "errada-123", "ip")
    caso.executar("diego@mail.com", "senha-forte", "ip")
    for _ in range(2):  # recomeça do zero
        with pytest.raises(NaoAutenticado):
            caso.executar("diego@mail.com", "errada-123", "ip")


def test_email_inexistente_tambem_gasta_tempo_de_conferencia(usuarios):
    hash_senha = FakeHash()
    caso = FazerLogin(usuarios, hash_senha, FakeTokens(), FakeLimitador())
    with pytest.raises(NaoAutenticado):
        caso.executar("ninguem@mail.com", "qualquer-coisa", "ip")
    assert hash_senha.simulacoes == 1
