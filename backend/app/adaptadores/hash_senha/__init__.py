import hashlib
import hmac
import os


class HashScrypt:
    """Hash de senha com scrypt (biblioteca padrão do Python), com sal aleatório."""

    def gerar(self, senha: str) -> str:
        sal = os.urandom(16)
        h = hashlib.scrypt(senha.encode(), salt=sal, n=2**14, r=8, p=1)
        return f"scrypt${sal.hex()}${h.hex()}"

    def simular(self, senha: str) -> None:
        """Faz o mesmo trabalho de conferir(), para o tempo de resposta não revelar se o e-mail existe."""
        self.conferir(senha, _HASH_FALSO)

    def conferir(self, senha: str, senha_hash: str) -> bool:
        try:
            _, sal, esperado = senha_hash.split("$")
            h = hashlib.scrypt(senha.encode(), salt=bytes.fromhex(sal), n=2**14, r=8, p=1)
            return hmac.compare_digest(h.hex(), esperado)
        except (ValueError, TypeError):
            return False


_HASH_FALSO = HashScrypt().gerar("hash-falso-so-para-gastar-tempo")
