class ErroDeDominio(Exception):
    """Base dos erros de regra de negócio. `codigo` é estável (o front traduz)."""

    def __init__(self, codigo: str, mensagem: str):
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem


class DadosInvalidos(ErroDeDominio):
    pass


class Conflito(ErroDeDominio):
    pass


class NaoEncontrado(ErroDeDominio):
    pass


class NaoAutenticado(ErroDeDominio):
    pass


class FonteExternaIndisponivel(ErroDeDominio):
    pass


class LimiteExcedido(ErroDeDominio):
    pass
