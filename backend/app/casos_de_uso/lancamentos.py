class ListarLancamentos:
    def __init__(self, lancamentos):
        self.lancamentos = lancamentos

    def executar(self):
        return self.lancamentos.listar()


class AtualizarLancamentos:
    """Usado pela rotina agendada. Se a fonte falhar, o erro sobe e os dados antigos ficam."""

    def __init__(self, fonte, lancamentos):
        self.fonte = fonte
        self.lancamentos = lancamentos

    def executar(self) -> int:
        novos = self.fonte.proximos()  # pode levantar FonteExternaIndisponivel
        self.lancamentos.substituir_todos(novos)
        return len(novos)
