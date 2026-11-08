import pytest

from app.casos_de_uso.avaliacoes import AvaliarJogo
from app.casos_de_uso.jogos import (CadastrarJogo, EditarJogo, ExcluirJogo, ListarJogos,
                                    RestaurarJogo)
from app.casos_de_uso.lancamentos import AtualizarLancamentos, ListarLancamentos
from app.casos_de_uso.visoes import FiltroJogos
from app.dominio.entidades import DadosJogo, Lancamento
from app.dominio.erros import Conflito, DadosInvalidos, FonteExternaIndisponivel, NaoEncontrado
from tests.fakes import (PNG, FakeAvaliacoes, FakeCapas, FakeFonte, FakeJogos, FakeLancamentos,
                         FakeReferencias)


@pytest.fixture
def mundo():
    class M: pass
    m = M()
    m.jogos, m.capas, m.refs, m.aval = FakeJogos(), FakeCapas(), FakeReferencias(), FakeAvaliacoes()
    m.cadastrar = CadastrarJogo(m.jogos, m.refs, m.capas)
    m.editar = EditarJogo(m.jogos, m.refs, m.capas)
    m.excluir = ExcluirJogo(m.jogos, m.refs, m.capas)
    m.restaurar = RestaurarJogo(m.jogos, m.refs, m.capas)
    return m


def dados(**kw):
    base = dict(nome="Fifa 18", ano=2017, genero_id=1, faixa_etaria_id=1, console_ids=[1])
    base.update(kw)
    return DadosJogo(**base)


def test_cadastra_jogo_guardando_quem_cadastrou(mundo):
    v = mundo.cadastrar.executar(5, dados())
    assert v.nome == "Fifa 18" and mundo.jogos.itens[v.id].cadastrado_por_id == 5


def test_cadastra_com_capa_guarda_o_arquivo(mundo):
    v = mundo.cadastrar.executar(5, dados(), capa=PNG)
    assert v.capa in mundo.capas.arquivos


def test_nome_repetido_gera_conflito_e_nao_guarda_capa(mundo):
    mundo.cadastrar.executar(5, dados())
    with pytest.raises(Conflito) as erro:
        mundo.cadastrar.executar(6, dados(nome="fifa 18"), capa=PNG)
    assert erro.value.codigo == "jogo_nome_repetido" and mundo.capas.arquivos == {}


def test_capa_invalida_nao_salva_o_jogo(mundo):
    with pytest.raises(DadosInvalidos):
        mundo.cadastrar.executar(5, dados(), capa=b"nao-e-imagem")
    assert mundo.jogos.itens == {}


def test_genero_inexistente(mundo):
    with pytest.raises(DadosInvalidos) as erro:
        mundo.cadastrar.executar(5, dados(genero_id=99))
    assert erro.value.codigo == "jogo_genero"


def test_qualquer_usuario_edita_e_fica_registrado(mundo):
    v = mundo.cadastrar.executar(5, dados())
    mundo.editar.executar(8, v.id, dados(nome="Fifa 19", ano=2018))
    j = mundo.jogos.itens[v.id]
    assert j.nome == "Fifa 19" and j.alterado_por_id == 8 and j.cadastrado_por_id == 5


def test_editar_troca_capa_e_remove_a_antiga(mundo):
    v = mundo.cadastrar.executar(5, dados(), capa=PNG)
    antiga = v.capa
    novo = mundo.editar.executar(5, v.id, dados(), capa=PNG + b"1")
    assert novo.capa != antiga and antiga not in mundo.capas.arquivos


def test_editar_para_nome_de_outro_jogo_conflita(mundo):
    mundo.cadastrar.executar(5, dados(nome="A"))
    b = mundo.cadastrar.executar(5, dados(nome="B"))
    with pytest.raises(Conflito):
        mundo.editar.executar(5, b.id, dados(nome="A"))


def test_exclusao_marcada_some_da_lista_e_restaura(mundo):
    v = mundo.cadastrar.executar(5, dados())
    mundo.excluir.executar(9, v.id)
    listar = ListarJogos(mundo.jogos)
    assert listar.executar() == []
    assert len(listar.executar(FiltroJogos(incluir_excluidos=True))) == 1
    assert mundo.jogos.itens[v.id].excluido_por_id == 9
    mundo.restaurar.executar(9, v.id)
    assert len(listar.executar()) == 1


def test_restaurar_com_nome_ja_ocupado_conflita(mundo):
    v = mundo.cadastrar.executar(5, dados())
    mundo.excluir.executar(5, v.id)
    mundo.cadastrar.executar(5, dados())
    with pytest.raises(Conflito):
        mundo.restaurar.executar(5, v.id)


def test_nao_edita_jogo_excluido_nem_inexistente(mundo):
    v = mundo.cadastrar.executar(5, dados())
    mundo.excluir.executar(5, v.id)
    for jid in (v.id, 99):
        with pytest.raises(NaoEncontrado):
            mundo.editar.executar(5, jid, dados())


def test_filtros(mundo):
    mundo.cadastrar.executar(1, dados(nome="Fifa 18"))
    mundo.cadastrar.executar(1, dados(nome="Final Fantasy X", genero_id=2, console_ids=[2]))
    listar = ListarJogos(mundo.jogos)
    assert [j.nome for j in listar.executar(FiltroJogos(texto="final"))] == ["Final Fantasy X"]
    assert [j.nome for j in listar.executar(FiltroJogos(genero_id=1))] == ["Fifa 18"]
    assert [j.nome for j in listar.executar(FiltroJogos(console_id=2))] == ["Final Fantasy X"]


def test_avaliar_substitui_a_avaliacao_anterior(mundo):
    v = mundo.cadastrar.executar(1, dados())
    avaliar = AvaliarJogo(mundo.jogos, mundo.aval)
    avaliar.executar(2, v.id, 5, "ótimo")
    avaliar.executar(2, v.id, 3)
    assert len(mundo.aval.itens) == 1 and mundo.aval.obter(2, v.id).nota == 3
    with pytest.raises(DadosInvalidos):
        avaliar.executar(2, v.id, 9)
    with pytest.raises(NaoEncontrado):
        avaliar.executar(2, 99, 4)


def test_lancamentos_atualizam_e_falha_mantem_os_antigos():
    repo = FakeLancamentos()
    novo = Lancamento("Jogo X", None, "PC", "RAWG")
    assert AtualizarLancamentos(FakeFonte([novo]), repo).executar() == 1
    with pytest.raises(FonteExternaIndisponivel):
        AtualizarLancamentos(FakeFonte(falha=True), repo).executar()
    assert ListarLancamentos(repo).executar() == [novo]
