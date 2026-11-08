import io

import pytest
from fastapi.testclient import TestClient

from app.config import SEGREDO_PADRAO, Config
from app.main import criar_app
from tests.rotas.test_api import cadastrar_e_logar


def test_cabecalhos_de_seguranca(cliente):
    r = cliente.get("/saude")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in r.headers["content-security-policy"]


def test_respostas_de_login_nao_ficam_em_cache(cliente):
    r = cliente.post("/auth/login", json={"email": "a@b.com", "senha": "x"})
    assert r.headers["cache-control"] == "no-store"


def test_forca_bruta_no_login_e_bloqueada(cliente):
    cadastrar_e_logar(cliente)
    anonimo = TestClient(cliente.app)
    for _ in range(5):
        assert anonimo.post("/auth/login", json={"email": "diego@mail.com", "senha": "errada-123"}).status_code == 401
    r = anonimo.post("/auth/login", json={"email": "diego@mail.com", "senha": "senha-forte"})
    assert r.status_code == 429 and r.json()["codigo"] == "muitas_tentativas"


def test_pedido_de_outra_origem_e_recusado(cliente):
    r = cliente.post("/auth/login", json={"email": "a@b.com", "senha": "x"}, headers={"Origin": "http://site-malicioso.com"})
    assert r.status_code == 403 and r.json()["codigo"] == "origem_invalida"
    r = cliente.post("/auth/login", json={"email": "a@b.com", "senha": "x"}, headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 401  # origem permitida: chega até a regra de login


def test_upload_gigante_e_barrado_antes_de_processar(cliente):
    cadastrar_e_logar(cliente)
    grande = io.BytesIO(b"\xff\xd8\xff" + b"0" * (4 * 1024 * 1024))
    r = cliente.post("/jogos", data={"nome": "X", "ano": "2000", "genero_id": "1", "faixa_etaria_id": "1", "console_ids": ["1"]},
                     files={"capa": ("x.jpg", grande, "image/jpeg")})
    assert r.status_code == 413


def test_producao_nao_sobe_com_configuracao_fraca(tmp_path):
    cfg = Config()
    cfg.ambiente, cfg.database_url, cfg.pasta_capas = "producao", f"sqlite:///{tmp_path / 'x.db'}", str(tmp_path / "c")
    cfg.jwt_segredo, cfg.cookie_seguro, cfg.origens_front = SEGREDO_PADRAO, False, ["http://localhost:5173"]
    with pytest.raises(RuntimeError) as erro:
        criar_app(cfg)
    assert "JWT_SEGREDO" in str(erro.value) and "COOKIE_SEGURO" in str(erro.value) and "https://" in str(erro.value)
    cfg.jwt_segredo, cfg.cookie_seguro, cfg.origens_front = "s" * 40, True, ["https://jogoteca.exemplo"]
    assert criar_app(cfg)  # configuração correta sobe
