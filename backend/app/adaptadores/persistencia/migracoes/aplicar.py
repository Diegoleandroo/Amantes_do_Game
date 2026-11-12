"""Aplica as migrações do banco (a "história" da estrutura das tabelas) até a versão mais nova."""
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import inspect

PASTA = Path(__file__).parent
PRIMEIRA, SEGUNDA = "0001", "0002"


def _configuracao() -> AlembicConfig:
    cfg = AlembicConfig()
    cfg.set_main_option("script_location", str(PASTA))
    return cfg


def aplicar_migracoes(motor) -> None:
    """Leva o banco até a última versão. Seguro para rodar a cada início: só aplica o que falta."""
    cfg = _configuracao()
    with motor.begin() as conexao:
        cfg.attributes["connection"] = conexao
        _adotar_banco_anterior_ao_alembic(cfg, conexao)
        command.upgrade(cfg, "head")


def _adotar_banco_anterior_ao_alembic(cfg, conexao) -> None:
    """Bancos criados antes do Alembic já têm tabelas, mas não têm o registro de versão.
    Marcamos em qual versão eles estão, para o Alembic aplicar só o que realmente falta."""
    inspetor = inspect(conexao)
    tabelas = set(inspetor.get_table_names())
    if "alembic_version" in tabelas or "usuario" not in tabelas:
        return
    colunas = {c["name"] for c in inspetor.get_columns("lancamento")} if "lancamento" in tabelas else set()
    command.stamp(cfg, SEGUNDA if "capa_url" in colunas else PRIMEIRA)
