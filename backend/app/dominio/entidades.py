from dataclasses import dataclass, field
from datetime import date, datetime

from app.dominio.erros import Conflito, DadosInvalidos
from app.dominio.regras import ano_maximo


@dataclass
class Usuario:
    nome: str
    email: str
    senha_hash: str
    idioma: str = "pt"
    id: int | None = None


@dataclass(frozen=True)
class Genero:
    id: int
    nome: str


@dataclass(frozen=True)
class FaixaEtaria:
    id: int
    descricao: str


@dataclass(frozen=True)
class Console:
    id: int
    nome: str


@dataclass
class DadosJogo:
    """O que o usuário informa ao cadastrar ou editar um jogo."""

    nome: str
    ano: int
    genero_id: int
    faixa_etaria_id: int
    console_ids: list[int]
    historia: str | None = None


def validar_dados_jogo(d: DadosJogo) -> DadosJogo:
    nome = (d.nome or "").strip()
    if not 1 <= len(nome) <= 120:
        raise DadosInvalidos("jogo_nome", "O nome do jogo deve ter entre 1 e 120 caracteres.")
    if not isinstance(d.ano, int) or not 1950 <= d.ano <= ano_maximo():
        raise DadosInvalidos("jogo_ano", f"O ano deve estar entre 1950 e {ano_maximo()}.")
    historia = (d.historia or "").strip() or None
    if historia and len(historia) > 5000:
        raise DadosInvalidos("jogo_historia", "A história deve ter até 5000 caracteres.")
    consoles = sorted(set(d.console_ids or []))
    if not consoles:
        raise DadosInvalidos("jogo_console", "Escolha pelo menos um console.")
    return DadosJogo(nome, d.ano, d.genero_id, d.faixa_etaria_id, consoles, historia)


@dataclass
class Jogo:
    nome: str
    ano: int
    genero_id: int
    faixa_etaria_id: int
    console_ids: list[int]
    cadastrado_por_id: int
    historia: str | None = None
    capa: str | None = None
    id: int | None = None
    cadastrado_em: datetime | None = None
    alterado_por_id: int | None = None
    excluido_em: datetime | None = None
    excluido_por_id: int | None = None

    @property
    def excluido(self) -> bool:
        return self.excluido_em is not None

    def atualizar(self, dados: DadosJogo, usuario_id: int) -> None:
        self.nome = dados.nome
        self.ano = dados.ano
        self.genero_id = dados.genero_id
        self.faixa_etaria_id = dados.faixa_etaria_id
        self.console_ids = list(dados.console_ids)
        self.historia = dados.historia
        self.alterado_por_id = usuario_id

    def excluir(self, usuario_id: int, agora: datetime) -> None:
        if self.excluido:
            raise Conflito("jogo_ja_excluido", "Este jogo já foi excluído.")
        self.excluido_em = agora
        self.excluido_por_id = usuario_id

    def restaurar(self) -> None:
        if not self.excluido:
            raise Conflito("jogo_nao_excluido", "Este jogo não está excluído.")
        self.excluido_em = None
        self.excluido_por_id = None


@dataclass
class Avaliacao:
    usuario_id: int
    jogo_id: int
    nota: int
    comentario: str | None = None
    id: int | None = None
    criada_em: datetime | None = None


@dataclass
class Lancamento:
    nome: str
    data_lancamento: date | None
    plataformas: str
    origem: str
    atualizado_em: datetime | None = None
    capa_url: str | None = None
    id: int | None = None
