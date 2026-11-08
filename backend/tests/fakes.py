"""Implementações em memória das portas, para testar o núcleo sem banco nem web."""
from dataclasses import replace

from app.casos_de_uso.visoes import AvaliacaoVisao, FiltroJogos, JogoVisao, Referencias
from app.dominio.entidades import Console, FaixaEtaria, Genero
from app.dominio.erros import FonteExternaIndisponivel


class FakeUsuarios:
    def __init__(self):
        self.itens = {}

    def obter_por_id(self, usuario_id):
        return self.itens.get(usuario_id)

    def obter_por_email(self, email):
        return next((u for u in self.itens.values() if u.email == email), None)

    def salvar(self, usuario):
        if usuario.id is None:
            usuario.id = len(self.itens) + 1
        self.itens[usuario.id] = usuario
        return usuario


class FakeReferencias:
    def todas(self):
        return Referencias(
            generos=[Genero(1, "Ação"), Genero(2, "RPG")],
            faixas_etarias=[FaixaEtaria(1, "Livre"), FaixaEtaria(2, "18 anos")],
            consoles=[Console(1, "PC"), Console(2, "PlayStation 2")],
        )


class FakeJogos:
    def __init__(self, usuarios=None):
        self.itens = {}
        self.usuarios = usuarios

    def obter(self, jogo_id):
        j = self.itens.get(jogo_id)
        return replace(j, console_ids=list(j.console_ids)) if j else None

    def existe_nome_ativo(self, nome, ignorar_id=None):
        return any(j.nome.lower() == nome.lower() and not j.excluido and j.id != ignorar_id
                   for j in self.itens.values())

    def salvar(self, jogo):
        if jogo.id is None:
            jogo.id = len(self.itens) + 1
        self.itens[jogo.id] = replace(jogo, console_ids=list(jogo.console_ids))
        return jogo

    def _visao(self, j):
        refs = FakeReferencias().todas()
        return JogoVisao(
            id=j.id, nome=j.nome, ano=j.ano, historia=j.historia, capa=j.capa,
            genero_id=j.genero_id, genero=next(g.nome for g in refs.generos if g.id == j.genero_id),
            faixa_etaria_id=j.faixa_etaria_id,
            faixa_etaria=next(f.descricao for f in refs.faixas_etarias if f.id == j.faixa_etaria_id),
            console_ids=j.console_ids,
            consoles=[c.nome for c in refs.consoles if c.id in j.console_ids],
            cadastrado_por="alguém", cadastrado_em=j.cadastrado_em, alterado_por=None,
            excluido_em=j.excluido_em, excluido_por=None,
        )

    def visao(self, jogo_id):
        j = self.itens.get(jogo_id)
        return self._visao(j) if j else None

    def listar(self, filtro: FiltroJogos):
        r = []
        for j in self.itens.values():
            if j.excluido and not filtro.incluir_excluidos:
                continue
            if filtro.texto and filtro.texto.lower() not in j.nome.lower():
                continue
            if filtro.genero_id and j.genero_id != filtro.genero_id:
                continue
            if filtro.console_id and filtro.console_id not in j.console_ids:
                continue
            r.append(self._visao(j))
        return r


class FakeAvaliacoes:
    def __init__(self):
        self.itens = {}

    def obter(self, usuario_id, jogo_id):
        return self.itens.get((usuario_id, jogo_id))

    def salvar(self, avaliacao):
        self.itens[(avaliacao.usuario_id, avaliacao.jogo_id)] = avaliacao
        return avaliacao

    def listar_do_jogo(self, jogo_id):
        return [AvaliacaoVisao(a.usuario_id, "x", a.nota, a.comentario, a.criada_em)
                for a in self.itens.values() if a.jogo_id == jogo_id]


class FakeLancamentos:
    def __init__(self):
        self.itens = []

    def listar(self):
        return list(self.itens)

    def substituir_todos(self, lancamentos):
        self.itens = list(lancamentos)


class FakeCapas:
    def __init__(self):
        self.arquivos = {}

    def guardar(self, conteudo, extensao):
        nome = f"capa{len(self.arquivos) + 1}.{extensao}"
        self.arquivos[nome] = conteudo
        return nome

    def remover(self, nome):
        self.arquivos.pop(nome, None)


class FakeHash:
    def gerar(self, senha):
        return "hash:" + senha

    def conferir(self, senha, senha_hash):
        return senha_hash == "hash:" + senha

    def simular(self, senha):
        self.simulacoes = getattr(self, "simulacoes", 0) + 1


class FakeLimitador:
    def __init__(self, max_falhas=3):
        self.falhas, self.max = {}, max_falhas

    def bloqueado(self, chave):
        return self.falhas.get(chave, 0) >= self.max

    def registrar_falha(self, chave):
        self.falhas[chave] = self.falhas.get(chave, 0) + 1

    def limpar(self, chave):
        self.falhas.pop(chave, None)


class FakeTokens:
    def gerar(self, usuario_id):
        return f"token-{usuario_id}"

    def ler(self, token):
        return int(token.split("-")[1]) if token and token.startswith("token-") else None


class FakeFonte:
    def __init__(self, lancamentos=None, falha=False):
        self.lancamentos = lancamentos or []
        self.falha = falha

    def proximos(self):
        if self.falha:
            raise FonteExternaIndisponivel("fonte_fora", "Fonte fora do ar.")
        return self.lancamentos


PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 20
