from datetime import date, datetime, timedelta, timezone

import httpx

from app.dominio.entidades import Lancamento
from app.dominio.erros import FonteExternaIndisponivel


URL_CAPA_IGDB = "https://images.igdb.com/igdb/image/upload/t_cover_big/{imagem}.jpg"


class FonteRawg:
    """Busca os próximos lançamentos na API do RAWG (https://rawg.io/apidocs)."""

    URL = "https://api.rawg.io/api/games"

    def __init__(self, chave: str, dias_a_frente: int = 365, limite: int = 20, cliente=None):
        self.chave = chave
        self.dias = dias_a_frente
        self.limite = limite
        self.cliente = cliente

    def proximos(self) -> list[Lancamento]:
        if not self.chave:
            raise FonteExternaIndisponivel("rawg_sem_chave", "Defina RAWG_API_KEY para buscar lançamentos.")
        hoje = date.today()
        params = {
            "key": self.chave,
            "dates": f"{hoje.isoformat()},{(hoje + timedelta(days=self.dias)).isoformat()}",
            "ordering": "released",
            "page_size": self.limite,
        }
        try:
            if self.cliente:
                resposta = self.cliente.get(self.URL, params=params)
            else:
                with httpx.Client(timeout=15) as c:
                    resposta = c.get(self.URL, params=params)
            resposta.raise_for_status()
            itens = resposta.json()["results"]
        except (httpx.HTTPError, KeyError, ValueError) as erro:
            raise FonteExternaIndisponivel("rawg_fora", f"RAWG indisponível: {erro}") from erro
        agora = datetime.now(timezone.utc)
        return [
            Lancamento(
                nome=i["name"],
                data_lancamento=date.fromisoformat(i["released"]) if i.get("released") else None,
                plataformas=", ".join(p["platform"]["name"] for p in i.get("platforms") or []),
                origem="RAWG",
                atualizado_em=agora,
                capa_url=i.get("background_image"),
            )
            for i in itens
        ]


class FonteIgdb:
    """Busca no IGDB (https://api-docs.igdb.com) os jogos MAIS AGUARDADOS que serão lançados.

    O IGDB pertence à Twitch: primeiro troca-se o Client ID e o Client Secret por um token
    temporário, depois consulta-se a lista de jogos. A popularidade vem do campo `hypes`
    (quantas pessoas já seguem o jogo antes do lançamento).
    """

    URL_TOKEN = "https://id.twitch.tv/oauth2/token"
    URL_JOGOS = "https://api.igdb.com/v4/games"

    def __init__(self, client_id: str, client_secret: str, limite: int = 20, dias_a_frente: int = 365, cliente=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.limite = limite
        self.dias = dias_a_frente
        self.cliente = cliente

    def proximos(self) -> list[Lancamento]:
        if not self.client_id or not self.client_secret:
            raise FonteExternaIndisponivel(
                "igdb_sem_chave", "Defina TWITCH_CLIENT_ID e TWITCH_CLIENT_SECRET para buscar lançamentos.")
        try:
            if self.cliente:
                itens = self._buscar(self.cliente)
            else:
                with httpx.Client(timeout=15) as c:
                    itens = self._buscar(c)
            return self._converter(itens)
        except (httpx.HTTPError, KeyError, ValueError, TypeError) as erro:
            raise FonteExternaIndisponivel("igdb_fora", f"IGDB indisponível: {erro}") from erro

    def _buscar(self, c) -> list[dict]:
        resposta = c.post(self.URL_TOKEN, params={
            "client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "client_credentials"})
        resposta.raise_for_status()
        token = resposta.json()["access_token"]
        agora = int(datetime.now(timezone.utc).timestamp())
        fim = agora + self.dias * 86400
        consulta = (
            "fields name, first_release_date, hypes, cover.image_id, platforms.name; "
            f"where first_release_date > {agora} & first_release_date < {fim} & hypes > 0; "
            f"sort hypes desc; limit {self.limite};"
        )
        resposta = c.post(self.URL_JOGOS, content=consulta,
                          headers={"Client-ID": self.client_id, "Authorization": f"Bearer {token}"})
        resposta.raise_for_status()
        return resposta.json()

    def _converter(self, itens: list[dict]) -> list[Lancamento]:
        """Os mais aguardados, mostrados por ordem de data de lançamento."""
        agora = datetime.now(timezone.utc)
        lancamentos = []
        for i in itens:
            if not i.get("name") or not i.get("first_release_date"):
                continue
            imagem = (i.get("cover") or {}).get("image_id")
            plataformas = [p["name"] for p in i.get("platforms") or [] if p.get("name")]
            lancamentos.append(Lancamento(
                nome=i["name"],
                data_lancamento=datetime.fromtimestamp(i["first_release_date"], tz=timezone.utc).date(),
                plataformas=", ".join(plataformas), origem="IGDB", atualizado_em=agora,
                capa_url=URL_CAPA_IGDB.format(imagem=imagem) if imagem else None))
        return sorted(lancamentos, key=lambda l: l.data_lancamento)
