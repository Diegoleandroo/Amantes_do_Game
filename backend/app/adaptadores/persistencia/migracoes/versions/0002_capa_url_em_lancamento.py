"""Lançamentos passam a guardar o endereço da capa (capa_url).

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("lancamento", sa.Column("capa_url", sa.String(300), nullable=True))


def downgrade() -> None:
    op.drop_column("lancamento", "capa_url")
