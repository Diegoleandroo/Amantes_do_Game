"""Rotina agendada: busca os próximos lançamentos (IGDB ou RAWG) e grava no banco.

Rodar:  python -m app.rotina_lancamentos      (precisa de TWITCH_CLIENT_ID e TWITCH_CLIENT_SECRET, ou RAWG_API_KEY)
Agendar: Agendador de Tarefas do Windows ou cron, 1 vez por dia.
"""
import logging
import sys

from app.adaptadores.cliente_externo import FonteIgdb, FonteRawg
from app.adaptadores.persistencia.banco import criar_fabrica_de_sessoes, preparar_banco
from app.adaptadores.persistencia.repositorios import RepositorioLancamentoSql
from app.casos_de_uso.lancamentos import AtualizarLancamentos
from app.config import Config
from app.dominio.erros import FonteExternaIndisponivel
from app.logs import configurar_logs, evento


def main() -> int:
    cfg = Config()
    configurar_logs(cfg.log_nivel)
    motor, fabrica = criar_fabrica_de_sessoes(cfg.database_url)
    preparar_banco(motor, fabrica)
    # IGDB é a fonte principal; o RAWG fica como alternativa se só ele estiver configurado.
    if cfg.rawg_chave and not cfg.twitch_client_id:
        fonte = FonteRawg(cfg.rawg_chave)
    else:
        fonte = FonteIgdb(cfg.twitch_client_id, cfg.twitch_client_secret)
    with fabrica() as sessao:
        caso = AtualizarLancamentos(fonte, RepositorioLancamentoSql(sessao))
        try:
            total = caso.executar()
        except FonteExternaIndisponivel as erro:
            print(f"Não atualizou (os lançamentos antigos foram mantidos): {erro.mensagem}")
            evento(logging.ERROR, "rotina_lancamentos_falhou", motivo=erro.mensagem)
            return 1
    print(f"{total} lançamentos atualizados.")
    evento(logging.INFO, "rotina_lancamentos_ok", total=total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
