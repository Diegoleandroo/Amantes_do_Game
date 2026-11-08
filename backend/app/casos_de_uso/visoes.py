"""Formatos de leitura (o que as telas precisam ver), já com nomes em vez de ids."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class JogoVisao:
    id: int
    nome: str
    ano: int
    historia: str | None
    capa: str | None
    genero_id: int
    genero: str
    faixa_etaria_id: int
    faixa_etaria: str
    console_ids: list[int]
    consoles: list[str]
    cadastrado_por: str
    cadastrado_em: datetime | None
    alterado_por: str | None
    excluido_em: datetime | None
    excluido_por: str | None
    nota_media: float | None = None
    total_avaliacoes: int = 0


@dataclass
class AvaliacaoVisao:
    usuario_id: int
    usuario: str
    nota: int
    comentario: str | None
    criada_em: datetime | None


@dataclass
class FiltroJogos:
    texto: str | None = None
    genero_id: int | None = None
    faixa_etaria_id: int | None = None
    console_id: int | None = None
    ano: int | None = None
    incluir_excluidos: bool = False


@dataclass
class Referencias:
    generos: list = field(default_factory=list)
    faixas_etarias: list = field(default_factory=list)
    consoles: list = field(default_factory=list)
