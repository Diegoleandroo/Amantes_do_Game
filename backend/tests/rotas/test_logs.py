import json
import logging

from fastapi.testclient import TestClient

from app.config import Config
from app.logs import FormatoJson
from app.main import criar_app


def _eventos(caplog):
    return [r for r in caplog.records if r.name == "jogoteca"]


def test_requisicao_vira_um_log_com_numero_metodo_caminho_status_e_tempo(cliente, caplog):
    with caplog.at_level(logging.INFO, logger="jogoteca"):
        resposta = cliente.get("/referencias")
    registro = next(r for r in _eventos(caplog) if r.getMessage() == "requisicao")
    assert registro.dados["caminho"] == "/referencias" and registro.dados["metodo"] == "GET"
    assert registro.dados["status"] in (200, 401) and "ms" in registro.dados
    assert resposta.headers["X-Request-ID"] == registro.dados["id"]


def test_login_nao_grava_senha_nem_email_nos_logs(cliente, caplog):
    corpo = {"nome": "Ana", "email": "ana.segredo@exemplo.com", "senha": "SenhaMuitoSecreta123", "idioma": "pt"}
    with caplog.at_level(logging.DEBUG, logger="jogoteca"):
        cliente.post("/usuarios", json=corpo)
        cliente.post("/auth/login", json={"email": corpo["email"], "senha": corpo["senha"]})
        cliente.post("/auth/login", json={"email": corpo["email"], "senha": "errada-errada-errada"})
    saida = "\n".join(FormatoJson().format(r) for r in _eventos(caplog))
    assert "SenhaMuitoSecreta123" not in saida and "ana.segredo" not in saida and "errada-errada" not in saida
    assert "login_ok" in saida


def test_login_com_senha_errada_registra_o_codigo_e_o_ip(cliente, caplog):
    with caplog.at_level(logging.INFO, logger="jogoteca"):
        cliente.post("/auth/login", json={"email": "x@y.com", "senha": "qualquer-coisa"})
    registro = next(r for r in _eventos(caplog) if r.getMessage() == "requisicao")
    assert registro.dados["status"] == 401 and registro.dados["codigo"] and registro.dados["ip"]
    assert registro.levelno == logging.WARNING


def test_saude_nao_polui_os_logs(cliente, caplog):
    with caplog.at_level(logging.DEBUG, logger="jogoteca"):
        cliente.get("/saude")
    assert _eventos(caplog) == []


def test_erro_inesperado_vira_500_generico_e_fica_no_log(tmp_path, caplog):
    cfg = Config()
    cfg.database_url = f"sqlite:///{tmp_path / 'teste.db'}"
    cfg.pasta_capas = str(tmp_path / "capas")
    app = criar_app(cfg)

    @app.get("/quebra")
    def quebra():
        raise RuntimeError("detalhe interno que o usuario nao pode ver")

    cliente = TestClient(app, raise_server_exceptions=False)
    with caplog.at_level(logging.INFO, logger="jogoteca"):
        resposta = cliente.get("/quebra")
    assert resposta.status_code == 500
    assert "detalhe interno" not in resposta.text and resposta.json()["id"] == resposta.headers["X-Request-ID"]
    erro = next(r for r in _eventos(caplog) if r.getMessage() == "erro_nao_tratado")
    assert erro.levelno == logging.ERROR and erro.exc_info


def test_formato_json_gera_uma_linha_valida():
    registro = logging.LogRecord("jogoteca", logging.INFO, "", 0, "teste", None, None)
    registro.dados = {"a": 1, "texto": "ação"}
    linha = json.loads(FormatoJson().format(registro))
    assert linha["evento"] == "teste" and linha["nivel"] == "INFO" and linha["a"] == 1 and linha["texto"] == "ação"
