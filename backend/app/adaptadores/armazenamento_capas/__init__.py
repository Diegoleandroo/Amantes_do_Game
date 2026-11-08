import uuid
from pathlib import Path


class CapasEmPasta:
    """Guarda as capas numa pasta do servidor. Na entrega, troca-se por armazenamento em nuvem."""

    def __init__(self, pasta: str):
        self.pasta = Path(pasta)
        self.pasta.mkdir(parents=True, exist_ok=True)

    def guardar(self, conteudo: bytes, extensao: str) -> str:
        nome = f"{uuid.uuid4().hex}.{extensao}"
        (self.pasta / nome).write_bytes(conteudo)
        return nome

    def remover(self, nome: str) -> None:
        alvo = (self.pasta / nome).resolve()
        if alvo.parent == self.pasta.resolve() and alvo.exists():
            alvo.unlink()
