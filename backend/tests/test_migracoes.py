"""As migrações do Alembic precisam descrever exatamente as tabelas que o código usa."""
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from app.adaptadores.persistencia.migracoes.aplicar import aplicar_migracoes
from app.adaptadores.persistencia.modelos import Base


def _motor(tmp_path, nome="banco.db"):
    return create_engine(f"sqlite:///{tmp_path / nome}")


def test_migracoes_reproduzem_os_modelos_sem_diferenca(tmp_path):
    """Se alguém mudar modelos.py e esquecer de criar a migração, este teste falha."""
    motor = _motor(tmp_path)
    aplicar_migracoes(motor)
    with motor.connect() as conexao:
        diferencas = compare_metadata(MigrationContext.configure(conexao, opts={"compare_type": True}), Base.metadata)
    assert diferencas == []


def test_rodar_duas_vezes_nao_quebra_nem_duplica(tmp_path):
    motor = _motor(tmp_path)
    aplicar_migracoes(motor)
    aplicar_migracoes(motor)
    with motor.connect() as conexao:
        assert conexao.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002"


def test_banco_criado_antes_do_alembic_e_adotado_sem_perder_dados(tmp_path):
    motor = _motor(tmp_path)
    Base.metadata.create_all(motor)  # como o sistema criava o banco antes das migrações
    with motor.begin() as c:
        c.execute(text("INSERT INTO genero (nome) VALUES ('Ação')"))
    aplicar_migracoes(motor)
    with motor.connect() as c:
        assert c.execute(text("SELECT nome FROM genero")).scalar() == "Ação"
        assert c.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002"


def test_banco_muito_antigo_recebe_so_a_coluna_que_faltava(tmp_path):
    motor = _motor(tmp_path)
    aplicar_migracoes(motor)
    with motor.begin() as c:  # volta ao estado da versão 0001
        c.execute(text("ALTER TABLE lancamento DROP COLUMN capa_url"))
        c.execute(text("DROP TABLE alembic_version"))
    aplicar_migracoes(motor)
    assert "capa_url" in {col["name"] for col in inspect(motor).get_columns("lancamento")}
