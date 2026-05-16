"""Supabase migration runner — direkt psycopg2 ile SQL çalıştırır."""

import argparse
import logging
import sys
from pathlib import Path

import psycopg2

from db.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_pg_connection():
    settings = get_settings()
    if not settings.supabase_db_host:
        logger.error("SUPABASE_DB_HOST not set in .env")
        return None
    try:
        project_ref = settings.supabase_url.rstrip("/").split("/")[-1].split(".")[0]
        conn = psycopg2.connect(
            host=settings.supabase_db_host,
            port=6543,
            dbname=settings.supabase_db_name,
            user=f"{settings.supabase_db_user}.{project_ref}",
            password=settings.supabase_db_password,
            sslmode="require",
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error("Failed to connect to Supabase DB: %s", e)
        return None


def run_sql_file(conn, sql_path: Path) -> bool:
    sql = sql_path.read_text()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        logger.info("Migration applied: %s", sql_path.name)
        return True
    except Exception as e:
        logger.error("Migration failed: %s — %s", sql_path.name, e)
        conn.rollback()
        return False


def test_functions(conn) -> None:
    tests = [
        (
            "search_similar_images",
            """
            SELECT image_name, similarity, rank
            FROM search_similar_images(
                array_fill(0.0::float, ARRAY[1024])::vector,
                exclude_image_name := NULL,
                top_k := 3,
                min_similarity := 0.0
            )
            LIMIT 0
        """,
        ),
        (
            "search_similar_images_rich",
            """
            SELECT image_name, similarity, rank
            FROM search_similar_images_rich(
                array_fill(0.0::float, ARRAY[1024])::vector,
                exclude_image_name := NULL,
                top_k := 3,
                min_similarity := 0.0
            )
            LIMIT 0
        """,
        ),
    ]
    for name, sql in tests:
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            logger.info("Function OK: %s", name)
        except Exception as e:
            logger.error("Function FAIL: %s — %s", name, e)


def main():
    parser = argparse.ArgumentParser(description="Run Supabase SQL migrations")
    parser.add_argument(
        "migration", nargs="?", help="Migration file path or name (e.g. 004_similarity_search)"
    )
    parser.add_argument("--all", action="store_true", help="Run all pending migrations")
    parser.add_argument("--test", action="store_true", help="Test functions after migration")
    args = parser.parse_args()

    conn = get_pg_connection()
    if conn is None:
        sys.exit(1)

    migrations_dir = Path(__file__).resolve().parent / "migrations"

    if args.all:
        paths = sorted(migrations_dir.glob("*.sql"))
    elif args.migration:
        p = Path(args.migration)
        if not p.exists():
            p = migrations_dir / args.migration
            if not p.suffix:
                p = p.with_suffix(".sql")
        if not p.exists():
            logger.error("Migration not found: %s", args.migration)
            sys.exit(1)
        paths = [p]
    else:
        logger.error("Specify a migration file or --all")
        sys.exit(1)

    for sql_path in paths:
        run_sql_file(conn, sql_path)

    if args.test:
        test_functions(conn)

    conn.close()
    logger.info("Done")


if __name__ == "__main__":
    main()
