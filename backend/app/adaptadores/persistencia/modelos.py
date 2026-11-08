"""Tabelas do banco (espelham o diagrama ER)."""
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


jogo_console = Table(
    "jogo_console", Base.metadata,
    Column("jogo_id", ForeignKey("jogo.id"), primary_key=True),
    Column("console_id", ForeignKey("console.id"), primary_key=True),
)


class UsuarioModelo(Base):
    __tablename__ = "usuario"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    idioma: Mapped[str] = mapped_column(String(2), default="pt")


class GeneroModelo(Base):
    __tablename__ = "genero"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True)


class FaixaEtariaModelo(Base):
    __tablename__ = "faixa_etaria"
    id: Mapped[int] = mapped_column(primary_key=True)
    descricao: Mapped[str] = mapped_column(String(60), unique=True)


class ConsoleModelo(Base):
    __tablename__ = "console"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True)


class JogoModelo(Base):
    __tablename__ = "jogo"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    ano: Mapped[int] = mapped_column(Integer)
    historia: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa: Mapped[str | None] = mapped_column(String(80), nullable=True)
    cadastrado_em: Mapped[datetime] = mapped_column(DateTime)
    genero_id: Mapped[int] = mapped_column(ForeignKey("genero.id"))
    faixa_etaria_id: Mapped[int] = mapped_column(ForeignKey("faixa_etaria.id"))
    cadastrado_por_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    alterado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    excluido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    excluido_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)

    genero: Mapped[GeneroModelo] = relationship()
    faixa_etaria: Mapped[FaixaEtariaModelo] = relationship()
    consoles: Mapped[list[ConsoleModelo]] = relationship(secondary=jogo_console)


class AvaliacaoModelo(Base):
    __tablename__ = "avaliacao"
    __table_args__ = (UniqueConstraint("usuario_id", "jogo_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    jogo_id: Mapped[int] = mapped_column(ForeignKey("jogo.id"))
    nota: Mapped[int] = mapped_column(Integer)
    comentario: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime)


class LancamentoModelo(Base):
    __tablename__ = "lancamento"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    data_lancamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    plataformas: Mapped[str] = mapped_column(String(300), default="")
    origem: Mapped[str] = mapped_column(String(30))
    capa_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime)
