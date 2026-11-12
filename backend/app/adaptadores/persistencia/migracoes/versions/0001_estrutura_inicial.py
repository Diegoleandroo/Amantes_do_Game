"""Estrutura inicial: usuários, catálogos, jogos, avaliações e lançamentos.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(80), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("idioma", sa.String(2), nullable=False),
    )
    op.create_table("genero", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("nome", sa.String(60), nullable=False, unique=True))
    op.create_table("faixa_etaria", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("descricao", sa.String(60), nullable=False, unique=True))
    op.create_table("console", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("nome", sa.String(60), nullable=False, unique=True))
    op.create_table(
        "jogo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("historia", sa.Text(), nullable=True),
        sa.Column("capa", sa.String(80), nullable=True),
        sa.Column("cadastrado_em", sa.DateTime(), nullable=False),
        sa.Column("genero_id", sa.Integer(), sa.ForeignKey("genero.id"), nullable=False),
        sa.Column("faixa_etaria_id", sa.Integer(), sa.ForeignKey("faixa_etaria.id"), nullable=False),
        sa.Column("cadastrado_por_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("alterado_por_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True),
        sa.Column("excluido_em", sa.DateTime(), nullable=True),
        sa.Column("excluido_por_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True),
    )
    op.create_index("ix_jogo_nome", "jogo", ["nome"])
    op.create_table(
        "jogo_console",
        sa.Column("jogo_id", sa.Integer(), sa.ForeignKey("jogo.id"), primary_key=True),
        sa.Column("console_id", sa.Integer(), sa.ForeignKey("console.id"), primary_key=True),
    )
    op.create_table(
        "avaliacao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("jogo_id", sa.Integer(), sa.ForeignKey("jogo.id"), nullable=False),
        sa.Column("nota", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.String(1000), nullable=True),
        sa.Column("criada_em", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("usuario_id", "jogo_id"),
    )
    op.create_table(
        "lancamento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("data_lancamento", sa.Date(), nullable=True),
        sa.Column("plataformas", sa.String(300), nullable=False),
        sa.Column("origem", sa.String(30), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for tabela in ("lancamento", "avaliacao", "jogo_console", "jogo", "console", "faixa_etaria", "genero", "usuario"):
        op.drop_table(tabela)
