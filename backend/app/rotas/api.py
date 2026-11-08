from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile
from pydantic import BaseModel

from app.casos_de_uso.visoes import FiltroJogos
from app.dominio.entidades import DadosJogo
from app.dominio.regras import TAMANHO_MAX_CAPA
from app.rotas import formatos
from app.rotas.deps import COOKIE, Servicos, usuario_logado

router = APIRouter()


# ---------- usuários e login ----------
class NovoUsuario(BaseModel):
    nome: str
    email: str
    senha: str
    idioma: str = "pt"


class Credenciais(BaseModel):
    email: str
    senha: str


class NovoIdioma(BaseModel):
    idioma: str


@router.post("/usuarios", status_code=201)
def cadastrar_usuario(corpo: NovoUsuario, sv: Servicos = Depends()):
    return formatos.usuario(sv.cadastrar_usuario.executar(corpo.nome, corpo.email, corpo.senha, corpo.idioma))


@router.post("/auth/login")
def login(corpo: Credenciais, requisicao: Request, resposta: Response, sv: Servicos = Depends()):
    origem = requisicao.client.host if requisicao.client else ""
    usuario, token = sv.fazer_login.executar(corpo.email, corpo.senha, origem)
    resposta.set_cookie(COOKIE, token, httponly=True, samesite="lax", secure=sv.cfg.cookie_seguro,
                        max_age=sv.cfg.jwt_minutos * 60, path="/")
    return formatos.usuario(usuario)


@router.post("/auth/logout", status_code=204)
def logout(resposta: Response):
    resposta.delete_cookie(COOKIE, path="/")


@router.get("/auth/eu")
def quem_sou_eu(usuario=Depends(usuario_logado)):
    return formatos.usuario(usuario)


@router.put("/usuarios/eu/idioma")
def escolher_idioma(corpo: NovoIdioma, usuario=Depends(usuario_logado), sv: Servicos = Depends()):
    return formatos.usuario(sv.escolher_idioma.executar(usuario.id, corpo.idioma))


# ---------- jogos ----------
@router.get("/referencias")
def referencias(sv: Servicos = Depends()):
    return formatos.referencias(sv.referencias.executar())


@router.get("/jogos")
def listar_jogos(texto: str | None = None, genero_id: int | None = None, faixa_etaria_id: int | None = None,
                 console_id: int | None = None, ano: int | None = None, incluir_excluidos: bool = False,
                 _=Depends(usuario_logado), sv: Servicos = Depends()):
    filtro = FiltroJogos(texto, genero_id, faixa_etaria_id, console_id, ano, incluir_excluidos)
    return [formatos.jogo(v) for v in sv.listar_jogos.executar(filtro)]


def _ler_capa(capa: UploadFile | None) -> bytes | None:
    if capa is None or not capa.filename:
        return None
    conteudo = capa.file.read(TAMANHO_MAX_CAPA + 1)  # +1 para detectar arquivo grande demais
    return conteudo or None


@router.post("/jogos", status_code=201)
def cadastrar_jogo(nome: str = Form(...), ano: int = Form(...), genero_id: int = Form(...),
                   faixa_etaria_id: int = Form(...), console_ids: list[int] = Form(...),
                   historia: str | None = Form(None), capa: UploadFile | None = File(None),
                   usuario=Depends(usuario_logado), sv: Servicos = Depends()):
    dados = DadosJogo(nome, ano, genero_id, faixa_etaria_id, console_ids, historia)
    return formatos.jogo(sv.cadastrar_jogo.executar(usuario.id, dados, _ler_capa(capa)))


@router.get("/jogos/{jogo_id}")
def obter_jogo(jogo_id: int, _=Depends(usuario_logado), sv: Servicos = Depends()):
    return formatos.jogo(sv.obter_jogo.executar(jogo_id))


@router.put("/jogos/{jogo_id}")
def editar_jogo(jogo_id: int, nome: str = Form(...), ano: int = Form(...), genero_id: int = Form(...),
                faixa_etaria_id: int = Form(...), console_ids: list[int] = Form(...),
                historia: str | None = Form(None), capa: UploadFile | None = File(None),
                usuario=Depends(usuario_logado), sv: Servicos = Depends()):
    dados = DadosJogo(nome, ano, genero_id, faixa_etaria_id, console_ids, historia)
    return formatos.jogo(sv.editar_jogo.executar(usuario.id, jogo_id, dados, _ler_capa(capa)))


@router.delete("/jogos/{jogo_id}")
def excluir_jogo(jogo_id: int, usuario=Depends(usuario_logado), sv: Servicos = Depends()):
    return formatos.jogo(sv.excluir_jogo.executar(usuario.id, jogo_id))


@router.post("/jogos/{jogo_id}/restaurar")
def restaurar_jogo(jogo_id: int, usuario=Depends(usuario_logado), sv: Servicos = Depends()):
    return formatos.jogo(sv.restaurar_jogo.executar(usuario.id, jogo_id))


# ---------- avaliações (feedback) ----------
class NovaAvaliacao(BaseModel):
    nota: int
    comentario: str | None = None


@router.put("/jogos/{jogo_id}/avaliacao")
def avaliar_jogo(jogo_id: int, corpo: NovaAvaliacao, usuario=Depends(usuario_logado), sv: Servicos = Depends()):
    sv.avaliar_jogo.executar(usuario.id, jogo_id, corpo.nota, corpo.comentario)
    return formatos.jogo(sv.obter_jogo.executar(jogo_id))


@router.get("/jogos/{jogo_id}/avaliacoes")
def listar_avaliacoes(jogo_id: int, _=Depends(usuario_logado), sv: Servicos = Depends()):
    return [formatos.avaliacao(a) for a in sv.listar_avaliacoes.executar(jogo_id)]


# ---------- lançamentos do mercado ----------
@router.get("/lancamentos")
def lancamentos(_=Depends(usuario_logado), sv: Servicos = Depends()):
    return [formatos.lancamento(l) for l in sv.listar_lancamentos.executar()]

