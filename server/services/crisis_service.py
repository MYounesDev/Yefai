import csv
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_MOCK_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mock"
CATALOG_PATH = _MOCK_DIR / "spare_parts_catalog.csv"
SUPPLIERS_PATH = _MOCK_DIR / "suppliers.csv"
INVENTORY_PATH = _MOCK_DIR / "inventory_snapshots.csv"


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
