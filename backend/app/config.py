import os


SEGREDO_PADRAO = "troque-este-segredo-em-producao-0123456789"


class Config:
    """Configurações lidas do ambiente (variáveis de ambiente ou arquivo .env)."""

    # Por padrão usa um arquivo SQLite (roda sem instalar nada).
    # Para MySQL: DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/jogoteca
    ambiente = os.getenv("AMBIENTE", "desenvolvimento")  # use "producao" no servidor real
    database_url = os.getenv("DATABASE_URL", "sqlite:///./jogoteca.db")
    jwt_segredo = os.getenv("JWT_SEGREDO", SEGREDO_PADRAO)
    jwt_minutos = int(os.getenv("JWT_MINUTOS", "60"))
    cookie_seguro = os.getenv("COOKIE_SEGURO", "false").lower() == "true"
    origens_front = [o.strip() for o in os.getenv(
        "ORIGENS_FRONT", "http://localhost:5173,http://127.0.0.1:5173").split(",")]
    pasta_capas = os.getenv("PASTA_CAPAS", "armazenamento/capas")
    log_nivel = os.getenv("LOG_NIVEL", "INFO")  # DEBUG, INFO, WARNING ou ERROR
    rawg_chave = os.getenv("RAWG_API_KEY", "")
    # IGDB (pertence à Twitch): crie o aplicativo em https://dev.twitch.tv/console
    twitch_client_id = os.getenv("TWITCH_CLIENT_ID", "")
    twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET", "")

    def validar(self) -> None:
        """Em produção, o sistema se recusa a subir com configuração insegura."""
        if self.ambiente != "producao":
            return
        problemas = []
        if self.jwt_segredo == SEGREDO_PADRAO or len(self.jwt_segredo) < 32:
            problemas.append("JWT_SEGREDO precisa ser próprio e ter 32+ caracteres")
        if not self.cookie_seguro:
            problemas.append("COOKIE_SEGURO precisa ser true (HTTPS)")
        if any(o.startswith("http://") for o in self.origens_front):
            problemas.append("ORIGENS_FRONT precisa usar https://")
        if problemas:
            raise RuntimeError("Configuração insegura para produção: " + "; ".join(problemas))
