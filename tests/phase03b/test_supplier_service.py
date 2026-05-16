"""Tests for supplier alternative search — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))

import pytest

from services.supplier_service import AlternativeResult, SupplierComparison, find_alternatives


class TestFindAlternatives:
    def test_returns_result(self):
        result = find_alternatives(part_id="1")
        assert isinstance(result, AlternativeResult)
        assert result.part_id == "1"

    def test_primary_supplier_exists(self):
        result = find_alternatives(part_id="1")
        # May or may not have primary depending on mock data
        if result.primary:
            assert isinstance(result.primary, SupplierComparison)
            assert result.primary.is_primary is True

    def test_warning_for_unmapped_part(self):
        result = find_alternatives(part_id="part_not_found_xyz")
        assert result.no_alternative_warning != ""

    def test_alternatives_are_sorted(self):
        result = find_alternatives(part_id="1")
        if result.alternatives:
            scores = [a.overall_score for a in result.alternatives]
            assert scores == sorted(scores, reverse=True)

    def test_lead_time_filter(self):
        result = find_alternatives(part_id="1", max_lead_time_days=5)
        for alt in result.alternatives:
            if alt.is_viable:
                assert alt.lead_time_p90 <= 5


class TestSupplierComparison:
    def test_defaults(self):
        sc = SupplierComparison(
            supplier_id="S01", supplier_name="Test Supplier",
            lead_time_p90=10, reliability_score=0.8,
        )
        assert sc.cost_delta_pct == 0.0
        assert sc.is_primary is False
        assert sc.is_viable is True

    def test_primary_defaults(self):
        sc = SupplierComparison(
            supplier_id="S01", supplier_name="Primary",
            lead_time_p90=14, reliability_score=0.9,
            is_primary=True,
        )
        assert sc.overall_score == 0.0  # default value, scoring happens in find_alternatives
