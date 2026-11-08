from datetime import datetime, timedelta, timezone

import jwt


class TokenJwt:
    def __init__(self, segredo: str, minutos: int):
        self.segredo = segredo
        self.minutos = minutos

    def gerar(self, usuario_id: int) -> str:
        agora = datetime.now(timezone.utc)
        return jwt.encode(
            {"sub": str(usuario_id), "iat": agora, "exp": agora + timedelta(minutes=self.minutos)},
            self.segredo, algorithm="HS256",
        )

    def ler(self, token: str) -> int | None:
        try:
            return int(jwt.decode(token, self.segredo, algorithms=["HS256"])["sub"])
        except (jwt.PyJWTError, KeyError, ValueError):
            return None
