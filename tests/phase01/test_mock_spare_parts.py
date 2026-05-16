import tempfile
from pathlib import Path

import pandas as pd
import pytest

from etl.generate_mock_spare_parts import (
    generate_catalog,
    generate_suppliers,
    generate_inventory,
    generate_tickets_and_pos,
    compute_crisis_score,
    risk_level,
    generate_all,
    export_all,
)


def test_generate_catalog():
    df = generate_catalog(40)
    assert len(df) == 40
    assert set(df.columns) >= {"part_id", "part_name", "criticality", "demand_pattern"}
    assert set(df["criticality"].unique()) == {"A", "B", "C"}
    assert set(df["demand_pattern"].unique()) <= {"intermittent", "erratic", "lumpy", "smooth"}


def test_generate_suppliers():
    df = generate_suppliers(10)
    assert len(df) == 10
    assert set(df.columns) >= {"supplier_id", "supplier_name", "reliability_score"}
    assert all(0 <= s <= 1 for s in df["reliability_score"])


def test_generate_inventory():
    catalog = generate_catalog(40)
    df = generate_inventory(catalog)
    assert len(df) == 40
    assert set(df.columns) >= {"part_id", "on_hand", "on_order", "min_level", "max_level"}


def test_compute_crisis_score():
    score = compute_crisis_score(on_hand=0, min_level=5, lead_time_p90=30, criticality="A", reliability=0.6)
    assert 70 <= score <= 100

    score_low = compute_crisis_score(on_hand=10, min_level=3, lead_time_p90=3, criticality="C", reliability=0.95)
    assert score_low <= 40


def test_risk_level():
    assert risk_level(80) == "crisis"
    assert risk_level(50) == "at_risk"
    assert risk_level(20) == "watch"
    assert risk_level(5) == "none"


def test_generate_tickets_and_pos():
    catalog = generate_catalog(40)
    suppliers = generate_suppliers(10)
    inventory = generate_inventory(catalog)
    tickets, pos = generate_tickets_and_pos(catalog, inventory, suppliers)

    assert len(tickets) == 40
    assert "crisis_score" in tickets.columns
    assert "risk" in tickets.columns

    n_crisis = len(tickets[tickets["risk"] == "crisis"])
    n_at_risk = len(tickets[tickets["risk"] == "at_risk"])
    assert n_crisis > 0
    assert n_at_risk > 0


def test_export_all(tmp_path):
    catalog = generate_catalog(20)
    export_all(
        tmp_path / "mock",
        spare_parts_catalog=catalog,
    )
    exported = tmp_path / "mock" / "spare_parts_catalog.csv"
    assert exported.exists()
    df = pd.read_csv(exported)
    assert len(df) == 20
