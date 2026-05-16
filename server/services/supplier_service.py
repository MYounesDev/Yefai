"""Supplier service — Phase 3B.

Alternative supplier scoring and comparison for spare parts crisis.
"""

import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_MOCK_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mock"
SUPPLIERS_PATH = _MOCK_DIR / "suppliers.csv"
PART_SUPPLIERS_PATH = _MOCK_DIR / "part_suppliers.csv"


@dataclass
class SupplierComparison:
    """Comparison of a supplier against the primary."""

    supplier_id: str
    supplier_name: str
    lead_time_p90: int
    reliability_score: float
    cost_delta_pct: float = 0.0
    overall_score: float = 0.0
    is_primary: bool = False
    is_viable: bool = True


@dataclass
class AlternativeResult:
    """Result of alternative supplier search."""

    part_id: str
    part_name: str
    primary: SupplierComparison | None = None
    alternatives: list[SupplierComparison] = field(default_factory=list)
    no_alternative_warning: str = ""


def find_alternatives(
    part_id: str,
    max_lead_time_days: int = 0,
) -> AlternativeResult:
    """Find alternative suppliers for a part.

    Args:
        part_id: Catalog part identifier.
        max_lead_time_days: If set (>0), filters suppliers whose lead_time_p90
            exceeds this threshold as non-viable.

    Returns:
        AlternativeResult with primary and ranked alternatives.

    """
    all_suppliers = _load_suppliers()
    part_suppliers = _load_part_suppliers(part_id)
    if not part_suppliers:
        return AlternativeResult(
            part_id=part_id,
            part_name=part_id,
            no_alternative_warning="Part not found in supplier mapping",
        )

    # Find primary and candidate alternates
    primary_sid: str | None = None
    alt_sids: list[str] = []
    for ps in part_suppliers:
        if ps.get("is_primary", "").lower() == "true":
            primary_sid = ps.get("supplier_id", "")
        else:
            alt_sids.append(ps.get("supplier_id", ""))

    # Also include ALL non-primary suppliers as potential alternates
    # Even if not mapped, cascade to any supplier that could work
    primary = _lookup_supplier(primary_sid, all_suppliers) if primary_sid else None

    alt_results: list[SupplierComparison] = []
    for sid in alt_sids:
        sup = _lookup_supplier(sid, all_suppliers)
        if sup is None:
            continue
        cost_delta = _estimate_cost_delta(sid, primary_sid)
        lead_time = int(sup.get("lead_time_p90", 14))
        reliability = float(sup.get("reliability_score", 0.5))

        score = _score_alternative(lead_time, reliability, cost_delta, max_lead_time_days)

        viable = True
        if max_lead_time_days > 0 and lead_time > max_lead_time_days:
            viable = False

        alt_results.append(
            SupplierComparison(
                supplier_id=sid,
                supplier_name=sup.get("supplier_name", sid),
                lead_time_p90=lead_time,
                reliability_score=reliability,
                cost_delta_pct=round(cost_delta, 1),
                overall_score=round(score, 2),
                is_primary=False,
                is_viable=viable,
            )
        )

    # Sort by overall score descending
    alt_results.sort(key=lambda s: s.overall_score, reverse=True)

    warning = ""
    if not alt_results:
        warning = "Bu parca icin alternatif tedarikci bulunamadi"
    elif not any(a.is_viable for a in alt_results):
        warning = "Alternatif tedarikcilerin hicbiri lead time kosulunu karsilamiyor"

    part_name = part_id  # will be resolved from catalog elsewhere

    return AlternativeResult(
        part_id=part_id,
        part_name=part_name,
        primary=SupplierComparison(
            supplier_id=primary_sid or "",
            supplier_name=primary.get("supplier_name", "Unknown") if primary else "Unknown",
            lead_time_p90=int(primary.get("lead_time_p90", 14)) if primary else 0,
            reliability_score=float(primary.get("reliability_score", 0.0)) if primary else 0.0,
            cost_delta_pct=0.0,
            overall_score=100.0,
            is_primary=True,
        )
        if primary
        else None,
        alternatives=alt_results,
        no_alternative_warning=warning,
    )


def _score_alternative(lead_time: int, reliability: float, cost_delta: float, max_lt: int) -> float:
    """Score an alternative supplier (0-100)."""
    # Lead time score: shorter is better (max 40 pts)
    if lead_time == 0:
        lt_score = 0
    elif max_lt > 0:
        lt_score = max(0, min(40, (1 - lead_time / max_lt) * 40))
    else:
        lt_score = max(0, min(40, (1 - lead_time / 60) * 40))

    # Reliability score: higher is better (max 40 pts)
    rel_score = reliability * 40

    # Cost delta: cheaper is better (max 20 pts), more expensive penalized
    cost_score = max(0, min(20, 20 - cost_delta * 0.2))

    return lt_score + rel_score + cost_score


def _estimate_cost_delta(supplier_id: str, primary_id: str | None) -> float:
    """Estimate cost difference from primary supplier (mock: ±20%)."""
    import hashlib

    seed = f"{supplier_id}:{primary_id or 'none'}"
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    # Range: -15% to +25%
    return (h % 41) - 15


def _lookup_supplier(supplier_id: str, all_suppliers: list[dict]) -> dict | None:
    for s in all_suppliers:
        if s.get("supplier_id", "") == supplier_id:
            return s
    return None


def _load_suppliers() -> list[dict]:
    if not SUPPLIERS_PATH.exists():
        return []
    with open(SUPPLIERS_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_part_suppliers(part_id: str) -> list[dict]:
    if not PART_SUPPLIERS_PATH.exists():
        return []
    result = []
    with open(PART_SUPPLIERS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("part_id", "") == part_id:
                result.append(row)
    return result
