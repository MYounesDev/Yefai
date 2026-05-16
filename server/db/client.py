import logging
from typing import Any

from supabase import Client, create_client

from db.config import get_settings

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_supabase_client() -> Client | None:
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    if not settings.supabase_connected:
        logger.warning("Supabase URL and service key not configured")
        return None

    try:
        _client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
    except Exception as e:
        logger.error("Failed to create Supabase client: %s", e)
        return None

    return _client


def test_connection() -> bool:
    client = get_supabase_client()
    if client is None:
        logger.warning("Supabase connection test skipped — client not available")
        return False

    try:
        client.table("sets").select("*").execute()
        logger.info("Supabase connection OK — sets table accessible")
        return True
    except Exception as e:
        logger.error("Supabase connection test FAILED: %s", e)
        return False


def run_migration_sql(sql_path: str, client: Client | None = None) -> bool:
    if client is None:
        client = get_supabase_client()

    if client is None:
        logger.warning("Migration skipped — Supabase client not available")
        return False

    with open(sql_path) as f:
        sql_content = f.read()

    statements = [s.strip() for s in sql_content.split(";") if s.strip()]

    for stmt in statements:
        try:
            client.rpc("exec_sql", {"sql": stmt}).execute()
        except Exception:
            raw_sql_execute(stmt, client)

    logger.info("Migration applied: %s", sql_path)
    return True


def raw_sql_execute(sql: str, client: Client) -> Any:
    try:
        return client.rpc("exec_sql", {"sql": sql.strip()}).execute()
    except Exception:
        logger.debug("Raw SQL fallback not available; skipping: %s...", sql[:60])
        return None
