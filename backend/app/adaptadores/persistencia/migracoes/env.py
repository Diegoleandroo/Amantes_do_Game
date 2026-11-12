"""Ambiente do Alembic. Duas formas de uso:

1. Pelo sistema: `aplicar_migracoes(motor)` entrega uma conexão pronta (config.attributes["connection"]).
2. Pela linha de comando (`alembic upgrade head`, `alembic revision --autogenerate`): usa DATABASE_URL.
"""
from alembic import context
from sqlalchemy import create_engine

from app.adaptadores.persistencia.modelos import Base
from app.config import Config

config = context.config
alvo = Base.metadata


def _rodar(conexao) -> None:
    context.configure(connection=conexao, target_metadata=alvo, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


conexao_pronta = config.attributes.get("connection")
if conexao_pronta is not None:
    _rodar(conexao_pronta)
else:
    motor = create_engine(Config().database_url)
    with motor.connect() as conexao:
        _rodar(conexao)
