import sqlite3
from pathlib import Path

import pytest


def test_migration_file_exists():
    migration_path = (
        Path(__file__).resolve().parent.parent.parent
        / "server"
        / "db"
        / "migrations"
        / "001_initial_schema.sql"
    )
    assert migration_path.exists(), f"Migration file not found: {migration_path}"

    content = migration_path.read_text()

    assert "CREATE TABLE" in content.upper()
    assert "sets" in content.lower()
    assert "images" in content.lower()
    assert "anomalies" in content.lower()
    assert "vector" in content.lower()
    assert "hnsw" in content.lower()
    assert "spare_parts_catalog" in content.lower()
    assert "suppliers" in content.lower()
    assert "inventory_snapshots" in content.lower()
    assert "part_tickets" in content.lower()
    assert "purchase_orders" in content.lower()


def test_migration_no_blob():
    migration_path = (
        Path(__file__).resolve().parent.parent.parent
        / "server"
        / "db"
        / "migrations"
        / "001_initial_schema.sql"
    )
    content = migration_path.read_text().upper()
    migration_raw = migration_path.read_text()

    assert "BYTEA" not in content
    assert "image_data" not in migration_raw.lower()
    assert "sensor_data" not in migration_raw.lower()

    non_comment = "\n".join(
        line for line in migration_raw.split("\n") if not line.strip().startswith("--")
    )
    assert "BLOB" not in non_comment.upper()
