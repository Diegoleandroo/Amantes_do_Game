from app.dominio.entidades import Usuario
from app.dominio.erros import Conflito, LimiteExcedido, NaoAutenticado, NaoEncontrado
from app.dominio.regras import (
    normalizar_email,
    validar_idioma,
    validar_nome_usuario,
    validar_senha,
)


class CadastrarUsuario:
    def __init__(self, usuarios, hash_senha):
        self.usuarios = usuarios
        self.hash_senha = hash_senha

    def executar(self, nome: str, email: str, senha: str, idioma: str = "pt") -> Usuario:
        nome = validar_nome_usuario(nome)
        email = normalizar_email(email)
        validar_senha(senha)
        validar_idioma(idioma)
        if self.usuarios.obter_por_email(email):
            raise Conflito("email_em_uso", "Já existe um usuário com este e-mail.")
        usuario = Usuario(nome=nome, email=email, senha_hash=self.hash_senha.gerar(senha), idioma=idioma)
        return self.usuarios.salvar(usuario)


class FazerLogin:
    def __init__(self, usuarios, hash_senha, tokens, limitador):
        self.usuarios = usuarios
        self.hash_senha = hash_senha
        self.tokens = tokens
        self.limitador = limitador

    def executar(self, email: str, senha: str, origem: str = "") -> tuple[Usuario, str]:
        email = (email or "").strip().lower()
        chave = f"{origem}|{email}"
        if self.limitador.bloqueado(chave):
            raise LimiteExcedido("muitas_tentativas", "Muitas tentativas. Aguarde alguns minutos e tente de novo.")
        usuario = self.usuarios.obter_por_email(email)
        if usuario:
            senha_certa = self.hash_senha.conferir(senha or "", usuario.senha_hash)
        else:
            self.hash_senha.simular(senha or "")  # mesmo tempo de resposta, exista o e-mail ou não
            senha_certa = False
        # Mesma resposta para e-mail inexistente e senha errada: não revela qual e-mail existe.
        if not senha_certa:
            self.limitador.registrar_falha(chave)
            raise NaoAutenticado("credenciais_invalidas", "E-mail ou senha incorretos.")
        self.limitador.limpar(chave)
        return usuario, self.tokens.gerar(usuario.id)


class IdentificarUsuario:
    """Transforma o token da requisição no usuário logado."""

    def __init__(self, usuarios, tokens):
        self.usuarios = usuarios
        self.tokens = tokens

    def executar(self, token: str | None) -> Usuario:
        usuario_id = self.tokens.ler(token) if token else None
        usuario = self.usuarios.obter_por_id(usuario_id) if usuario_id else None
        if not usuario:
            raise NaoAutenticado("nao_autenticado", "Faça login para continuar.")
        return usuario


class EscolherIdioma:
    def __init__(self, usuarios):
        self.usuarios = usuarios

    def executar(self, usuario_id: int, idioma: str) -> Usuario:
        validar_idioma(idioma)
        usuario = self.usuarios.obter_por_id(usuario_id)
        if not usuario:
            raise NaoEncontrado("usuario_nao_encontrado", "Usuário não encontrado.")
        usuario.idioma = idioma
        return self.usuarios.salvar(usuario)
