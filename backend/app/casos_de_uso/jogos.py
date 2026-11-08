from datetime import datetime, timezone

from app.casos_de_uso.visoes import FiltroJogos, JogoVisao, Referencias
from app.dominio.entidades import DadosJogo, Jogo, validar_dados_jogo
from app.dominio.erros import Conflito, DadosInvalidos, NaoEncontrado
from app.dominio.regras import descobrir_extensao_capa


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _conferir_referencias(refs: Referencias, d: DadosJogo) -> None:
    if d.genero_id not in {g.id for g in refs.generos}:
        raise DadosInvalidos("jogo_genero", "Gênero inválido.")
    if d.faixa_etaria_id not in {f.id for f in refs.faixas_etarias}:
        raise DadosInvalidos("jogo_faixa", "Faixa etária inválida.")
    validos = {c.id for c in refs.consoles}
    if not set(d.console_ids) <= validos:
        raise DadosInvalidos("jogo_console", "Console inválido.")


class _CasoDeUsoJogo:
    def __init__(self, jogos, referencias, capas):
        self.jogos = jogos
        self.referencias = referencias
        self.capas = capas

    def _obter_ativo(self, jogo_id: int) -> Jogo:
        jogo = self.jogos.obter(jogo_id)
        if not jogo or jogo.excluido:
            raise NaoEncontrado("jogo_nao_encontrado", "Jogo não encontrado.")
        return jogo

    def _guardar_capa(self, conteudo: bytes) -> str:
        extensao = descobrir_extensao_capa(conteudo)
        return self.capas.guardar(conteudo, extensao)


class CadastrarJogo(_CasoDeUsoJogo):
    """Segue o diagrama de atividade: valida → nome repetido? → salva → guarda capa."""

    def executar(self, usuario_id: int, dados: DadosJogo, capa: bytes | None = None) -> JogoVisao:
        dados = validar_dados_jogo(dados)
        _conferir_referencias(self.referencias.todas(), dados)
        if capa:
            descobrir_extensao_capa(capa)  # recusa capa ruim antes de salvar o jogo
        if self.jogos.existe_nome_ativo(dados.nome):
            raise Conflito("jogo_nome_repetido", "Já existe um jogo com este nome.")
        jogo = self.jogos.salvar(
            Jogo(
                nome=dados.nome, ano=dados.ano, historia=dados.historia,
                genero_id=dados.genero_id, faixa_etaria_id=dados.faixa_etaria_id,
                console_ids=list(dados.console_ids), cadastrado_por_id=usuario_id,
            )
        )
        if capa:
            jogo.capa = self._guardar_capa(capa)
            jogo = self.jogos.salvar(jogo)
        return self.jogos.visao(jogo.id)


class EditarJogo(_CasoDeUsoJogo):
    def executar(self, usuario_id: int, jogo_id: int, dados: DadosJogo, capa: bytes | None = None) -> JogoVisao:
        jogo = self._obter_ativo(jogo_id)
        dados = validar_dados_jogo(dados)
        _conferir_referencias(self.referencias.todas(), dados)
        if capa:
            descobrir_extensao_capa(capa)
        if self.jogos.existe_nome_ativo(dados.nome, ignorar_id=jogo.id):
            raise Conflito("jogo_nome_repetido", "Já existe um jogo com este nome.")
        jogo.atualizar(dados, usuario_id)
        capa_antiga = jogo.capa
        if capa:
            jogo.capa = self._guardar_capa(capa)
        self.jogos.salvar(jogo)
        if capa and capa_antiga:
            self.capas.remover(capa_antiga)
        return self.jogos.visao(jogo.id)


class ExcluirJogo(_CasoDeUsoJogo):
    """Exclusão marcada: o jogo some das listas, mas continua no banco e pode voltar."""

    def executar(self, usuario_id: int, jogo_id: int) -> JogoVisao:
        jogo = self.jogos.obter(jogo_id)
        if not jogo:
            raise NaoEncontrado("jogo_nao_encontrado", "Jogo não encontrado.")
        jogo.excluir(usuario_id, _agora())
        self.jogos.salvar(jogo)
        return self.jogos.visao(jogo.id)


class RestaurarJogo(_CasoDeUsoJogo):
    def executar(self, usuario_id: int, jogo_id: int) -> JogoVisao:
        jogo = self.jogos.obter(jogo_id)
        if not jogo:
            raise NaoEncontrado("jogo_nao_encontrado", "Jogo não encontrado.")
        if self.jogos.existe_nome_ativo(jogo.nome, ignorar_id=jogo.id):
            raise Conflito("jogo_nome_repetido", "Já existe um jogo ativo com este nome.")
        jogo.restaurar()
        jogo.alterado_por_id = usuario_id
        self.jogos.salvar(jogo)
        return self.jogos.visao(jogo.id)


class ListarJogos:
    def __init__(self, jogos):
        self.jogos = jogos

    def executar(self, filtro: FiltroJogos | None = None) -> list[JogoVisao]:
        return self.jogos.listar(filtro or FiltroJogos())


class ObterJogo:
    def __init__(self, jogos):
        self.jogos = jogos

    def executar(self, jogo_id: int) -> JogoVisao:
        visao = self.jogos.visao(jogo_id)
        if not visao:
            raise NaoEncontrado("jogo_nao_encontrado", "Jogo não encontrado.")
        return visao


class ListarReferencias:
    def __init__(self, referencias):
        self.referencias = referencias

    def executar(self) -> Referencias:
        return self.referencias.todas()
