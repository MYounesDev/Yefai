from pathlib import Path


def test_config_file_exists():
    config_path = (
        Path(__file__).resolve().parent.parent.parent / "server" / "db" / "config.py"
    )
    assert config_path.exists()


def test_client_file_exists():
    client_path = (
        Path(__file__).resolve().parent.parent.parent / "server" / "db" / "client.py"
    )
    assert client_path.exists()


def test_config_settings_loads():
    from db.config import Settings

    settings = Settings()
    assert hasattr(settings, "supabase_url")
    assert hasattr(settings, "supabase_service_key")


def test_client_creates_without_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "")

    import db.client as c

    c._client = None

    client = c.get_supabase_client()
    assert client is None
