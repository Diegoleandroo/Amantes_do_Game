import time
from collections import defaultdict, deque


class LimitadorEmMemoria:
    """Bloqueia uma chave (IP + e-mail) após várias falhas seguidas, por um tempo.

    Fica na memória de UM processo: serve para uma instância só. Com várias instâncias da API,
    troque por um adaptador com Redis (a porta é a mesma).
    """

    def __init__(self, max_falhas: int = 5, janela_segundos: int = 900, relogio=time.monotonic):
        self.max_falhas = max_falhas
        self.janela = janela_segundos
        self.relogio = relogio
        self._falhas: dict[str, deque] = defaultdict(deque)

    def _podar(self, chave: str) -> deque:
        fila = self._falhas[chave]
        limite = self.relogio() - self.janela
        while fila and fila[0] <= limite:
            fila.popleft()
        return fila

    def bloqueado(self, chave: str) -> bool:
        return len(self._podar(chave)) >= self.max_falhas

    def registrar_falha(self, chave: str) -> None:
        self._podar(chave).append(self.relogio())

    def limpar(self, chave: str) -> None:
        self._falhas.pop(chave, None)
