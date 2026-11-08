"""Raiz de composição: aqui (e só aqui) os casos de uso são ligados aos adaptadores."""
from fastapi import Depends, Request

from app.adaptadores.hash_senha import HashScrypt
from app.adaptadores.persistencia.repositorios import (
    RepositorioAvaliacaoSql, RepositorioJogoSql, RepositorioLancamentoSql,
    RepositorioReferenciasSql, RepositorioUsuarioSql)
from app.adaptadores.token_jwt import TokenJwt
from app.casos_de_uso.avaliacoes import AvaliarJogo, ListarAvaliacoes
from app.casos_de_uso.jogos import (CadastrarJogo, EditarJogo, ExcluirJogo, ListarJogos,
                                    ListarReferencias, ObterJogo, RestaurarJogo)
from app.casos_de_uso.lancamentos import ListarLancamentos
from app.casos_de_uso.usuarios import (CadastrarUsuario, EscolherIdioma, FazerLogin,
                                       IdentificarUsuario)

COOKIE = "jogoteca_token"


def sessao(request: Request):
    with request.app.state.fabrica() as s:
        yield s


class Servicos:
    def __init__(self, request: Request, s=Depends(sessao)):
        cfg = request.app.state.config
        self.cfg = cfg
        capas = request.app.state.capas
        usuarios, jogos = RepositorioUsuarioSql(s), RepositorioJogoSql(s)
        refs, avals = RepositorioReferenciasSql(s), RepositorioAvaliacaoSql(s)
        hash_senha, tokens = HashScrypt(), TokenJwt(cfg.jwt_segredo, cfg.jwt_minutos)
        self.cadastrar_usuario = CadastrarUsuario(usuarios, hash_senha)
        self.fazer_login = FazerLogin(usuarios, hash_senha, tokens, request.app.state.limitador)
        self.identificar = IdentificarUsuario(usuarios, tokens)
        self.escolher_idioma = EscolherIdioma(usuarios)
        self.cadastrar_jogo = CadastrarJogo(jogos, refs, capas)
        self.editar_jogo = EditarJogo(jogos, refs, capas)
        self.excluir_jogo = ExcluirJogo(jogos, refs, capas)
        self.restaurar_jogo = RestaurarJogo(jogos, refs, capas)
        self.listar_jogos = ListarJogos(jogos)
        self.obter_jogo = ObterJogo(jogos)
        self.referencias = ListarReferencias(refs)
        self.avaliar_jogo = AvaliarJogo(jogos, avals)
        self.listar_avaliacoes = ListarAvaliacoes(avals)
        self.listar_lancamentos = ListarLancamentos(RepositorioLancamentoSql(s))


def usuario_logado(request: Request, servicos: Servicos = Depends()):
    return servicos.identificar.executar(request.cookies.get(COOKIE))
