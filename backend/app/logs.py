"""Registro de eventos (logs) em JSON, uma linha por evento, na saída padrão.

Por que JSON: ferramentas de hospedagem e de alerta leem e filtram esse formato.
Por que na saída padrão: o Docker guarda e mostra (`docker compose logs api`).

Regra de ouro: NUNCA registrar senha, token, e-mail, cookie ou o conteúdo do que o usuário enviou.
"""
import json
import logging
import sys
from datetime import datetime, timezone

NOME = "jogoteca"


class FormatoJson(logging.Formatter):
    def format(self, registro: logging.LogRecord) -> str:
        linha = {
            "quando": datetime.fromtimestamp(registro.created, timezone.utc).isoformat(timespec="milliseconds"),
            "nivel": registro.levelname,
            "evento": registro.getMessage(),
        }
        linha.update(getattr(registro, "dados", {}))
        if registro.exc_info:
            linha["excecao"] = self.formatException(registro.exc_info)
        return json.dumps(linha, ensure_ascii=False)


def configurar_logs(nivel: str = "INFO") -> logging.Logger:
    registro = logging.getLogger(NOME)
    registro.setLevel(nivel.upper())
    if not any(getattr(h, "_jogoteca", False) for h in registro.handlers):
        manipulador = logging.StreamHandler(sys.stdout)
        manipulador.setFormatter(FormatoJson())
        manipulador._jogoteca = True
        registro.addHandler(manipulador)
    return registro


def log() -> logging.Logger:
    return logging.getLogger(NOME)


def evento(nivel: int, nome: str, **dados) -> None:
    log().log(nivel, nome, extra={"dados": dados})
