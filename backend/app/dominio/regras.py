"""Regras de validação puras: não dependem de banco, web nem arquivos."""
import re
from datetime import date

from app.dominio.erros import DadosInvalidos

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
IDIOMAS = ("pt", "en")
TAMANHO_MAX_CAPA = 2 * 1024 * 1024  # 2 MB


def validar_nome_usuario(nome: str) -> str:
    nome = (nome or "").strip()
    if not 2 <= len(nome) <= 80:
        raise DadosInvalidos("nome_invalido", "O nome deve ter entre 2 e 80 caracteres.")
    return nome


def normalizar_email(email: str) -> str:
    email = (email or "").strip().lower()
    if len(email) > 254 or not EMAIL_RE.match(email):
        raise DadosInvalidos("email_invalido", "E-mail inválido.")
    return email


def validar_senha(senha: str) -> str:
    if not senha or len(senha) < 8:
        raise DadosInvalidos("senha_curta", "A senha deve ter pelo menos 8 caracteres.")
    if len(senha) > 128:
        raise DadosInvalidos("senha_longa", "A senha deve ter no máximo 128 caracteres.")
    return senha


def validar_idioma(idioma: str) -> str:
    if idioma not in IDIOMAS:
        raise DadosInvalidos("idioma_invalido", "Idioma inválido.")
    return idioma


def validar_nota(nota: int) -> int:
    if not isinstance(nota, int) or not 1 <= nota <= 5:
        raise DadosInvalidos("nota_invalida", "A nota deve ser de 1 a 5.")
    return nota


def validar_comentario(comentario: str | None) -> str | None:
    comentario = (comentario or "").strip() or None
    if comentario and len(comentario) > 1000:
        raise DadosInvalidos("comentario_longo", "O comentário deve ter até 1000 caracteres.")
    return comentario


def descobrir_extensao_capa(conteudo: bytes) -> str:
    """Confere tamanho e tipo real da imagem (pelo cabeçalho do arquivo)."""
    if len(conteudo) > TAMANHO_MAX_CAPA:
        raise DadosInvalidos("capa_grande", "A capa deve ter no máximo 2 MB.")
    if conteudo.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return "webp"
    raise DadosInvalidos("capa_tipo", "A capa deve ser uma imagem JPG, PNG ou WEBP.")


def ano_maximo() -> int:
    return date.today().year + 1
