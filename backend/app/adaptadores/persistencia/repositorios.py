from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.adaptadores.persistencia.modelos import (
    AvaliacaoModelo, ConsoleModelo, FaixaEtariaModelo, GeneroModelo, JogoModelo,
    LancamentoModelo, UsuarioModelo)
from app.casos_de_uso.visoes import AvaliacaoVisao, FiltroJogos, JogoVisao, Referencias
from app.dominio.entidades import (Avaliacao, Console, FaixaEtaria, Genero, Jogo, Lancamento,
                                   Usuario)


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # guardado em UTC, sem fuso


class RepositorioUsuarioSql:
    def __init__(self, sessao: Session):
        self.s = sessao

    @staticmethod
    def _para_dominio(m: UsuarioModelo | None) -> Usuario | None:
        return Usuario(m.nome, m.email, m.senha_hash, m.idioma, m.id) if m else None

    def obter_por_id(self, usuario_id):
        return self._para_dominio(self.s.get(UsuarioModelo, usuario_id))

    def obter_por_email(self, email):
        return self._para_dominio(self.s.scalar(select(UsuarioModelo).where(UsuarioModelo.email == email)))

    def salvar(self, usuario):
        m = self.s.get(UsuarioModelo, usuario.id) if usuario.id else UsuarioModelo()
        m.nome, m.email, m.senha_hash, m.idioma = usuario.nome, usuario.email, usuario.senha_hash, usuario.idioma
        self.s.add(m)
        self.s.commit()
        usuario.id = m.id
        return usuario


class RepositorioReferenciasSql:
    def __init__(self, sessao: Session):
        self.s = sessao

    def todas(self):
        return Referencias(
            generos=[Genero(g.id, g.nome) for g in self.s.scalars(select(GeneroModelo).order_by(GeneroModelo.nome))],
            faixas_etarias=[FaixaEtaria(f.id, f.descricao) for f in self.s.scalars(select(FaixaEtariaModelo).order_by(FaixaEtariaModelo.id))],
            consoles=[Console(c.id, c.nome) for c in self.s.scalars(select(ConsoleModelo).order_by(ConsoleModelo.id))],
        )


class RepositorioJogoSql:
    def __init__(self, sessao: Session):
        self.s = sessao

    def obter(self, jogo_id):
        m = self.s.get(JogoModelo, jogo_id)
        if not m:
            return None
        return Jogo(
            nome=m.nome, ano=m.ano, genero_id=m.genero_id, faixa_etaria_id=m.faixa_etaria_id,
            console_ids=sorted(c.id for c in m.consoles), cadastrado_por_id=m.cadastrado_por_id,
            historia=m.historia, capa=m.capa, id=m.id, cadastrado_em=m.cadastrado_em,
            alterado_por_id=m.alterado_por_id, excluido_em=m.excluido_em, excluido_por_id=m.excluido_por_id)

    def existe_nome_ativo(self, nome, ignorar_id=None):
        q = select(JogoModelo.id).where(func.lower(JogoModelo.nome) == nome.lower(), JogoModelo.excluido_em.is_(None))
        if ignorar_id:
            q = q.where(JogoModelo.id != ignorar_id)
        return self.s.scalar(q.limit(1)) is not None

    def salvar(self, jogo):
        m = self.s.get(JogoModelo, jogo.id) if jogo.id else JogoModelo(cadastrado_em=_agora())
        m.nome, m.ano, m.historia, m.capa = jogo.nome, jogo.ano, jogo.historia, jogo.capa
        m.genero_id, m.faixa_etaria_id = jogo.genero_id, jogo.faixa_etaria_id
        m.cadastrado_por_id, m.alterado_por_id = jogo.cadastrado_por_id, jogo.alterado_por_id
        m.excluido_em, m.excluido_por_id = jogo.excluido_em, jogo.excluido_por_id
        if m.excluido_em is not None and m.excluido_em.tzinfo is not None:
            m.excluido_em = m.excluido_em.astimezone(timezone.utc).replace(tzinfo=None)
        m.consoles = list(self.s.scalars(select(ConsoleModelo).where(ConsoleModelo.id.in_(jogo.console_ids))))
        self.s.add(m)
        self.s.commit()
        jogo.id, jogo.cadastrado_em = m.id, m.cadastrado_em
        return jogo

    # ---- leitura (telas) ----
    def _visoes(self, modelos: list[JogoModelo]) -> list[JogoVisao]:
        if not modelos:
            return []
        ids_usuarios = {u for m in modelos for u in (m.cadastrado_por_id, m.alterado_por_id, m.excluido_por_id) if u}
        nomes = dict(self.s.execute(select(UsuarioModelo.id, UsuarioModelo.nome).where(UsuarioModelo.id.in_(ids_usuarios))).all())
        medias = {j: (round(float(media), 1), total) for j, media, total in self.s.execute(
            select(AvaliacaoModelo.jogo_id, func.avg(AvaliacaoModelo.nota), func.count())
            .where(AvaliacaoModelo.jogo_id.in_([m.id for m in modelos])).group_by(AvaliacaoModelo.jogo_id)).all()}
        r = []
        for m in modelos:
            media, total = medias.get(m.id, (None, 0))
            cons = sorted(m.consoles, key=lambda c: c.id)
            r.append(JogoVisao(
                id=m.id, nome=m.nome, ano=m.ano, historia=m.historia, capa=m.capa,
                genero_id=m.genero_id, genero=m.genero.nome,
                faixa_etaria_id=m.faixa_etaria_id, faixa_etaria=m.faixa_etaria.descricao,
                console_ids=[c.id for c in cons], consoles=[c.nome for c in cons],
                cadastrado_por=nomes.get(m.cadastrado_por_id, "?"), cadastrado_em=m.cadastrado_em,
                alterado_por=nomes.get(m.alterado_por_id), excluido_em=m.excluido_em,
                excluido_por=nomes.get(m.excluido_por_id), nota_media=media, total_avaliacoes=total))
        return r

    def visao(self, jogo_id):
        m = self.s.get(JogoModelo, jogo_id)
        return self._visoes([m])[0] if m else None

    def listar(self, filtro: FiltroJogos):
        q = select(JogoModelo).options(selectinload(JogoModelo.consoles), selectinload(JogoModelo.genero),
                                       selectinload(JogoModelo.faixa_etaria)).order_by(func.lower(JogoModelo.nome))
        if not filtro.incluir_excluidos:
            q = q.where(JogoModelo.excluido_em.is_(None))
        if filtro.texto:
            q = q.where(JogoModelo.nome.ilike(f"%{filtro.texto.strip()}%"))
        if filtro.genero_id:
            q = q.where(JogoModelo.genero_id == filtro.genero_id)
        if filtro.faixa_etaria_id:
            q = q.where(JogoModelo.faixa_etaria_id == filtro.faixa_etaria_id)
        if filtro.ano:
            q = q.where(JogoModelo.ano == filtro.ano)
        if filtro.console_id:
            q = q.where(JogoModelo.consoles.any(ConsoleModelo.id == filtro.console_id))
        return self._visoes(list(self.s.scalars(q)))


class RepositorioAvaliacaoSql:
    def __init__(self, sessao: Session):
        self.s = sessao

    def obter(self, usuario_id, jogo_id):
        m = self.s.scalar(select(AvaliacaoModelo).where(
            AvaliacaoModelo.usuario_id == usuario_id, AvaliacaoModelo.jogo_id == jogo_id))
        return Avaliacao(m.usuario_id, m.jogo_id, m.nota, m.comentario, m.id, m.criada_em) if m else None

    def salvar(self, a):
        m = self.s.get(AvaliacaoModelo, a.id) if a.id else AvaliacaoModelo(
            usuario_id=a.usuario_id, jogo_id=a.jogo_id, criada_em=_agora())
        m.nota, m.comentario = a.nota, a.comentario
        self.s.add(m)
        self.s.commit()
        a.id, a.criada_em = m.id, m.criada_em
        return a

    def listar_do_jogo(self, jogo_id):
        linhas = self.s.execute(
            select(AvaliacaoModelo, UsuarioModelo.nome).join(UsuarioModelo, UsuarioModelo.id == AvaliacaoModelo.usuario_id)
            .where(AvaliacaoModelo.jogo_id == jogo_id).order_by(AvaliacaoModelo.criada_em.desc())).all()
        return [AvaliacaoVisao(a.usuario_id, nome, a.nota, a.comentario, a.criada_em) for a, nome in linhas]


class RepositorioLancamentoSql:
    def __init__(self, sessao: Session):
        self.s = sessao

    def listar(self):
        ms = self.s.scalars(select(LancamentoModelo).order_by(LancamentoModelo.data_lancamento.is_(None), LancamentoModelo.data_lancamento))
        return [Lancamento(m.nome, m.data_lancamento, m.plataformas, m.origem, m.atualizado_em, m.capa_url, m.id) for m in ms]

    def substituir_todos(self, lancamentos):
        """Troca tudo de uma vez: ou grava a lista nova inteira, ou nada muda."""
        try:
            self.s.execute(delete(LancamentoModelo))
            agora = _agora()
            self.s.add_all(LancamentoModelo(nome=l.nome, data_lancamento=l.data_lancamento,
                                            plataformas=l.plataformas, origem=l.origem, capa_url=l.capa_url, atualizado_em=agora)
                           for l in lancamentos)
            self.s.commit()
        except Exception:
            self.s.rollback()
            raise
