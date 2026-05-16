"""Crisis Service — calculates crisis scores, auto-orders, and handles supplier management."""

import csv
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from supabase import Client

from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

# --- MAIN FILE CONSTANTS ---
_MOCK_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mock"
CATALOG_PATH = _MOCK_DIR / "spare_parts_catalog.csv"
SUPPLIERS_PATH = _MOCK_DIR / "suppliers.csv"
INVENTORY_PATH = _MOCK_DIR / "inventory_snapshots.csv"


# --- MAIN FILE DATACLASSES ---
@dataclass
class CrisisInput:
    part_id: int
    anomaly_score: float = 0.0
    stock_gap_weight: float = 0.30
    lead_time_weight: float = 0.25
    criticality_weight: float = 0.20
    supplier_risk_weight: float = 0.15
    anomaly_weight: float = 0.10


@dataclass
class CrisisResult:
    image_id: int = 0
    part_id: int = 0
    part_name: str = ""
    crisis_score: float = 0.0
    risk_level: str = "none"
    breakdown: dict | None = None

    @property
    def needs_auto_order(self) -> bool:
        return self.risk_level in ("crisis", "at_risk")


# --- MAIN FILE SCORING LOGIC (Overrides ABC file's calculation) ---
def calculate_crisis_score(image_id: int, anomaly_score: float) -> CrisisResult:
    part = _find_related_part(image_id)
    if part is None:
        return CrisisResult(image_id=image_id, risk_level="none")

    inv = _get_inventory(part["part_id"])
    sup = _get_primary_supplier(part["part_id"])

    on_hand = int(inv.get("on_hand", 0) if inv else 0)
    min_level = int(inv.get("min_level", 10) if inv else 10)
    stock_gap = max(0.0, 1.0 - (on_hand / min_level if min_level > 0 else 1.0))

    lead_time_p90 = int(sup.get("lead_time_p90", 14) if sup else 14)

    criticality_map = {"A_vital": 1.0, "B_essential": 0.6, "C_desirable": 0.3}
    criticality = criticality_map.get(part.get("criticality", "C_desirable"), 0.3)

    reliability = float(sup.get("reliability_score", 0.8) if sup else 0.8)
    supplier_risk = 1.0 - reliability

    stock_gap_contrib = stock_gap * 100 * 0.30
    lead_time_contrib = min(1.0, lead_time_p90 / 30.0) * 100 * 0.25
    criticality_contrib = criticality * 100 * 0.20
    supplier_risk_contrib = supplier_risk * 100 * 0.15
    anomaly_contrib = anomaly_score * 100 * 0.10

    total = round(
        stock_gap_contrib
        + lead_time_contrib
        + criticality_contrib
        + supplier_risk_contrib
        + anomaly_contrib,
        1,
    )

    if total > 70:
        risk_level = "crisis"
    elif total > 40:
        risk_level = "at_risk"
    elif total > 20:
        risk_level = "watch"
    else:
        risk_level = "none"

    return CrisisResult(
        image_id=image_id,
        part_id=part.get("part_id", 0),
        part_name=part.get("part_name", ""),
        crisis_score=total,
        risk_level=risk_level,
        breakdown={
            "stock_gap_pct": round(stock_gap * 100, 1),
            "on_hand": on_hand,
            "min_level": min_level,
            "lead_time_p90_days": lead_time_p90,
            "criticality": part.get("criticality", ""),
            "supplier_reliability": reliability,
            "anomaly_score": anomaly_score,
            "contributions": {
                "stock_gap": round(stock_gap_contrib, 1),
                "lead_time": round(lead_time_contrib, 1),
                "criticality": round(criticality_contrib, 1),
                "supplier_risk": round(supplier_risk_contrib, 1),
                "anomaly": round(anomaly_contrib, 1),
            },
        },
    )


def _find_related_part(image_id: int) -> dict | None:
    catalog = _load_csv(CATALOG_PATH)
    if not catalog:
        return None
    idx = image_id % len(catalog)
    return catalog[idx]


def _get_inventory(part_id_raw: str | int) -> dict | None:
    rows = _load_csv(INVENTORY_PATH)
    part_id_str = str(part_id_raw)
    for r in rows:
        if str(r.get("part_id", "")) == part_id_str:
            return r
    return None


def _get_primary_supplier(part_id_raw: str | int) -> dict | None:
    rows = _load_csv(SUPPLIERS_PATH)
    for r in rows:
        if r.get("is_primary", "").lower() == "true":
            return r
    return rows[0] if rows else None


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        logger.warning("Mock CSV not found: %s", path)
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --- ABC FILE SERVICE (Retaining non-conflicting methods) ---
class CrisisService:
    def __init__(self, supabase: Client, prediction_service: PredictionService | None = None):
        self.supabase = supabase
        self.prediction_service = prediction_service or PredictionService(supabase)

    async def get_crisis_dashboard(self, org_id: str) -> dict[str, Any]:
        """Get org-wide crisis overview."""
        # We'd normally scan all parts or rely on precomputed scores
        # For this prototype we will return an aggregated mock
        return {
            "total_parts": 125,
            "at_risk_count": 5,
            "critical_count": 2,
            "top_crisis_parts": [
                {"part_id": "P-100", "score": 85, "risk_level": "critical"},
                {"part_id": "P-101", "score": 72, "risk_level": "at_risk"},
            ],
            "risk_distribution": {"safe": 100, "watch": 18, "at_risk": 5, "critical": 2},
        }

    async def calculate_crisis_score(self, org_id: str, part_id: str) -> dict[str, Any]:
        """Calculate a crisis score for a specific part (mock implementation)."""
        part = None
        for row in _load_csv(CATALOG_PATH):
            if str(row.get("part_id", "")) == str(part_id):
                part = row
                break

        if part is None:
            raise ValueError(f"Part not found: {part_id}")

        inv = _get_inventory(part_id)
        sup = _get_primary_supplier(part_id)

        on_hand = int(inv.get("on_hand", 0) if inv else 0)
        min_level = int(inv.get("min_level", 10) if inv else 10)
        stock_gap = max(0.0, 1.0 - (on_hand / min_level if min_level > 0 else 1.0))

        lead_time_p90 = int(sup.get("lead_time_p90", 14) if sup else 14)

        criticality_map = {"A_vital": 1.0, "B_essential": 0.6, "C_desirable": 0.3}
        criticality = criticality_map.get(part.get("criticality", "C_desirable"), 0.3)

        reliability = float(sup.get("reliability_score", 0.8) if sup else 0.8)
        supplier_risk = 1.0 - reliability

        stock_gap_contrib = stock_gap * 100 * 0.30
        lead_time_contrib = min(1.0, lead_time_p90 / 30.0) * 100 * 0.25
        criticality_contrib = criticality * 100 * 0.20
        supplier_risk_contrib = supplier_risk * 100 * 0.15

        total = round(
            stock_gap_contrib + lead_time_contrib + criticality_contrib + supplier_risk_contrib,
            1,
        )

        if total > 70:
            risk_level = "crisis"
        elif total > 40:
            risk_level = "at_risk"
        elif total > 20:
            risk_level = "watch"
        else:
            risk_level = "none"

        return {
            "part_id": part.get("part_id", part_id),
            "part_name": part.get("part_name", ""),
            "crisis_score": total,
            "risk_level": risk_level,
            "breakdown": {
                "stock_gap_pct": round(stock_gap * 100, 1),
                "on_hand": on_hand,
                "min_level": min_level,
                "lead_time_p90_days": lead_time_p90,
                "criticality": part.get("criticality", ""),
                "supplier_reliability": reliability,
                "contributions": {
                    "stock_gap": round(stock_gap_contrib, 1),
                    "lead_time": round(lead_time_contrib, 1),
                    "criticality": round(criticality_contrib, 1),
                    "supplier_risk": round(supplier_risk_contrib, 1),
                },
            },
        }

    async def create_auto_order(self, org_id: str, ticket_id: str) -> dict[str, Any]:
        """Auto-generate purchase order for a ticket."""
        ticket_res = (
            self.supabase.table("part_tickets")
            .select("*")
            .eq("ticket_id", ticket_id)
            .eq("org_id", org_id)
            .maybe_single()
            .execute()
        )
        if not ticket_res.data:
            raise ValueError(f"Ticket not found: {ticket_id}")

        part_id = ticket_res.data.get("part_id")
        quantity = ticket_res.data.get("required_quantity", 1)

        # Find best supplier
        supplier_res = (
            self.supabase.table("supplier_parts")
            .select("supplier_id, unit_cost")
            .eq("part_id", part_id)
            .eq("org_id", org_id)
            .order("is_preferred", desc=True)
            .limit(1)
            .execute()
        )

        supplier_id = None
        unit_cost = 100.0

        if supplier_res.data:
            supplier_id = supplier_res.data[0].get("supplier_id")
            unit_cost = supplier_res.data[0].get("unit_cost", 100.0)

        po_id = f"PO-{str(uuid.uuid4())[:8].upper()}"

        po_data = {
            "po_id": po_id,
            "org_id": org_id,
            "part_id": part_id,
            "supplier_id": supplier_id,
            "quantity": quantity,
            "unit_price": unit_cost,
            "status": "pending",
        }

        po_res = self.supabase.table("purchase_orders").insert(po_data).execute()

        if not po_res.data:
            raise ValueError("Failed to create Purchase Order")

        return po_res.data[0]

    async def get_alternative_suppliers(self, org_id: str, part_id: str) -> list[dict[str, Any]]:
        """Get alternative suppliers for a part."""
        res = (
            self.supabase.table("supplier_parts")
            .select(
                "supplier_id, unit_cost, lead_time_days, is_preferred, suppliers(name, reliability_score)"
            )
            .eq("part_id", part_id)
            .eq("org_id", org_id)
            .execute()
        )
        return res.data or []
