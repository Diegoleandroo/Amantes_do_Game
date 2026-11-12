import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.adaptadores.armazenamento_capas import CapasEmPasta
from app.adaptadores.limitador import LimitadorEmMemoria
from app.adaptadores.persistencia.banco import criar_fabrica_de_sessoes, preparar_banco
from app.config import Config
from app.dominio import erros
from app.logs import configurar_logs, evento
from app.rotas.api import router

STATUS = {
    erros.DadosInvalidos: 422,
    erros.Conflito: 409,
    erros.NaoEncontrado: 404,
    erros.NaoAutenticado: 401,
    erros.FonteExternaIndisponivel: 503,
    erros.LimiteExcedido: 429,
}
TAMANHO_MAX_REQUISICAO = 3 * 1024 * 1024  # a capa tem no máximo 2 MB; sobra folga para o formulário


def criar_app(config=None) -> FastAPI:
    cfg = config or Config()
    cfg.validar()
    configurar_logs(cfg.log_nivel)
    app = FastAPI(title="JogoTeca API")
    motor, fabrica = criar_fabrica_de_sessoes(cfg.database_url)
    preparar_banco(motor, fabrica)
    capas = CapasEmPasta(cfg.pasta_capas)
    app.state.config, app.state.fabrica, app.state.capas = cfg, fabrica, capas
    app.state.limitador = LimitadorEmMemoria()

    @app.middleware("http")
    async def cabecalhos_de_seguranca(request: Request, chamar):
        resposta = await chamar(request)
        resposta.headers["X-Content-Type-Options"] = "nosniff"  # o navegador não "adivinha" o tipo do arquivo
        resposta.headers["X-Frame-Options"] = "DENY"  # ninguém embute a API em outra página
        resposta.headers["Referrer-Policy"] = "no-referrer"
        resposta.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        if request.url.path.startswith(("/auth", "/usuarios")):
            resposta.headers["Cache-Control"] = "no-store"
        return resposta

    @app.middleware("http")
    async def limitar_tamanho(request: Request, chamar):
        tamanho = request.headers.get("content-length")
        if tamanho and tamanho.isdigit() and int(tamanho) > TAMANHO_MAX_REQUISICAO:
            return JSONResponse(status_code=413, content={"codigo": "requisicao_grande", "detalhe": "Requisição grande demais."})
        return await chamar(request)

    @app.middleware("http")
    async def conferir_origem(request: Request, chamar):
        # Defesa extra contra CSRF: pedidos que alteram dados só valem se vierem do nosso front-end.
        origem = request.headers.get("origin")
        if request.method not in ("GET", "HEAD", "OPTIONS") and origem and origem not in cfg.origens_front:
            return JSONResponse(status_code=403, content={"codigo": "origem_invalida", "detalhe": "Origem não permitida."})
        return await chamar(request)

    @app.middleware("http")
    async def registrar_requisicao(request: Request, chamar):
        """Dá um número a cada requisição, mede o tempo e registra o resultado. Erros inesperados viram 500 genérico."""
        numero = uuid.uuid4().hex[:12]
        inicio = time.perf_counter()
        try:
            resposta = await chamar(request)
        except Exception:
            logging.getLogger("jogoteca").exception(
                "erro_nao_tratado", extra={"dados": {"id": numero, "metodo": request.method, "caminho": request.url.path}})
            resposta = JSONResponse(status_code=500, content={
                "codigo": "erro_interno", "detalhe": "Erro interno. Informe o código ao suporte.", "id": numero})
        status = resposta.status_code
        resposta.headers["X-Request-ID"] = numero
        if request.url.path != "/saude":  # o Docker pergunta a cada 15 s; registrar seria ruído
            dados = {"id": numero, "metodo": request.method, "caminho": request.url.path, "status": status,
                     "ms": round((time.perf_counter() - inicio) * 1000)}
            codigo = getattr(request.state, "codigo_erro", None)
            if codigo:
                dados["codigo"] = codigo
            if status in (401, 403, 429) and request.client:
                dados["ip"] = request.client.host  # só em eventos de segurança
            nivel = logging.ERROR if status >= 500 else logging.WARNING if status >= 400 else logging.INFO
            evento(nivel, "requisicao", **dados)
        return resposta

    app.add_middleware(
        CORSMiddleware, allow_origins=cfg.origens_front, allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )

    @app.exception_handler(erros.ErroDeDominio)
    async def erro_de_dominio(request: Request, erro: erros.ErroDeDominio):
        request.state.codigo_erro = erro.codigo
        status = next((s for t, s in STATUS.items() if isinstance(erro, t)), 400)
        return JSONResponse(status_code=status, content={"codigo": erro.codigo, "detalhe": erro.mensagem})

    @app.get("/saude")
    def saude() -> dict:
        """Confere se a API está de pé."""
        return {"status": "ok"}

    app.include_router(router)
    app.mount("/capas", StaticFiles(directory=cfg.pasta_capas), name="capas")
    return app


app = criar_app()
