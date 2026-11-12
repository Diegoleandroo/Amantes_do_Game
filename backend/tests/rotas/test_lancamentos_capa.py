from datetime import date

from sqlalchemy import create_engine, text

from app.adaptadores.persistencia.banco import preparar_banco
from app.adaptadores.persistencia.repositorios import RepositorioLancamentoSql
from app.dominio.entidades import Lancamento
from tests.rotas.test_api import cadastrar_e_logar


def test_api_devolve_a_capa_do_lancamento(cliente):
    cadastrar_e_logar(cliente)
    with cliente.app.state.fabrica() as sessao:
        RepositorioLancamentoSql(sessao).substituir_todos([
            Lancamento("Com capa", date(2030, 1, 2), "PC", "IGDB", capa_url="https://exemplo.com/a.jpg"),
            Lancamento("Sem capa", None, "", "IGDB")])
    itens = {l["nome"]: l for l in cliente.get("/lancamentos").json()}
    assert itens["Com capa"]["capa_url"] == "https://exemplo.com/a.jpg"
    assert itens["Sem capa"]["capa_url"] is None


def test_banco_antigo_sem_a_coluna_capa_e_atualizado_sozinho(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'antigo.db'}")
    from app.adaptadores.persistencia.modelos import Base
    Base.metadata.create_all(motor)
    with motor.begin() as c:  # banco como era antes das capas: sem a coluna e sem registro do Alembic
        c.execute(text("ALTER TABLE lancamento DROP COLUMN capa_url"))
        c.execute(text("INSERT INTO lancamento (nome, plataformas, origem, atualizado_em) VALUES ('Velho', 'PC', 'RAWG', '2026-01-01')"))
    from sqlalchemy.orm import sessionmaker
    fabrica = sessionmaker(bind=motor, expire_on_commit=False)
    preparar_banco(motor, fabrica)
    with fabrica() as s:
        velho, = RepositorioLancamentoSql(s).listar()
    assert velho.nome == "Velho" and velho.capa_url is None
