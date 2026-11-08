import pytest
from fastapi.testclient import TestClient

from app.config import Config
from app.main import criar_app


@pytest.fixture
def cliente(tmp_path):
    cfg = Config()
    cfg.database_url = f"sqlite:///{tmp_path / 'teste.db'}"
    cfg.pasta_capas = str(tmp_path / "capas")
    return TestClient(criar_app(cfg))
