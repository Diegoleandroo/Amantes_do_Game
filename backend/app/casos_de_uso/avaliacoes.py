from datetime import datetime, timezone

from app.dominio.entidades import Avaliacao
from app.dominio.erros import NaoEncontrado
from app.dominio.regras import validar_comentario, validar_nota


class AvaliarJogo:
    """Um usuário tem uma avaliação por jogo; avaliar de novo substitui a anterior."""

    def __init__(self, jogos, avaliacoes):
        self.jogos = jogos
        self.avaliacoes = avaliacoes

    def executar(self, usuario_id: int, jogo_id: int, nota: int, comentario: str | None = None) -> Avaliacao:
        nota = validar_nota(nota)
        comentario = validar_comentario(comentario)
        jogo = self.jogos.obter(jogo_id)
        if not jogo or jogo.excluido:
            raise NaoEncontrado("jogo_nao_encontrado", "Jogo não encontrado.")
        existente = self.avaliacoes.obter(usuario_id, jogo_id)
        if existente:
            existente.nota, existente.comentario = nota, comentario
            return self.avaliacoes.salvar(existente)
        return self.avaliacoes.salvar(
            Avaliacao(usuario_id=usuario_id, jogo_id=jogo_id, nota=nota, comentario=comentario,
                      criada_em=datetime.now(timezone.utc))
        )


class ListarAvaliacoes:
    def __init__(self, avaliacoes):
        self.avaliacoes = avaliacoes

    def executar(self, jogo_id: int):
        return self.avaliacoes.listar_do_jogo(jogo_id)
