import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """每个测试用独立临时 DB，避免用例间串数据。"""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)
    monkeypatch.setattr("app.config.DB_PATH", db_path)
    from app import seed
    seed.init_db()
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
