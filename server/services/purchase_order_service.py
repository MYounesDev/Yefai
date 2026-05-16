"""Purchase Order service — Phase 3B.

Creates mock purchase orders on crisis detection with duplicate prevention.
"""

import csv
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

_MOCK_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mock"
CATALOG_PATH = _MOCK_DIR / "spare_parts_catalog.csv"
SUPPLIERS_PATH = _MOCK_DIR / "suppliers.csv"
PART_SUPPLIERS_PATH = _MOCK_DIR / "part_suppliers.csv"


@dataclass
class PurchaseOrder:
    """Represents a single purchase order."""

    po_id: int
    part_id: str = ""
    part_name: str = ""
    supplier_id: str = ""
    supplier_name: str = ""
    quantity: int = 1
    unit_price: float = 0.0
    total: float = 0.0
    lead_time_days: int = 0
    status: str = "draft"
    created_at: str = ""
    trigger: str = "crisis"


# In-memory store — resets on server restart (mock)
_purchase_orders: list[PurchaseOrder] = []
_next_po_id: int = 1000


def create_auto_order(
    part_id: str,
    quantity: int = 1,
    trigger: str = "crisis",
    force: bool = False,
) -> "PurchaseOrder":
    """Create a purchase order for a part with duplicate prevention."""
    global _next_po_id

    if not force and _has_recent_order(part_id):
        raise DuplicateOrderError(
            f"Duplicate order prevented for part_id={part_id} (last order < 24h)"
        )

    part = _find_part(part_id)
    supplier = _find_primary_supplier(part_id)

    unit_price = float(part.get("unit_cost", 0.0)) if part else 0.0
    supplier_name = supplier.get("supplier_name", "Unknown") if supplier else "Unknown"
    lead_time = int(supplier.get("lead_time_p90", 14)) if supplier else 14

    po = PurchaseOrder(
        po_id=_next_po_id,
        part_id=part_id,
        part_name=part.get("part_name", part_id) if part else part_id,
        supplier_id=supplier.get("supplier_id", "") if supplier else "",
        supplier_name=supplier_name,
        quantity=quantity,
        unit_price=unit_price,
        total=round(unit_price * quantity, 2),
        lead_time_days=lead_time,
        status="ready_for_review",
        created_at=datetime.now(UTC).isoformat(),
        trigger=trigger,
    )
    _next_po_id += 1
    _purchase_orders.append(po)
    logger.info("Auto PO #%d created for part_id=%s (total=%.2f)", po.po_id, part_id, po.total)
    return po


def get_purchase_orders(status: str | None = None, limit: int = 50) -> list[PurchaseOrder]:
    """List purchase orders, optionally filtered by status."""
    if status:
        return [po for po in _purchase_orders if po.status == status][:limit]
    return _purchase_orders[-limit:][::-1]  # newest first


def get_purchase_order(po_id: int) -> PurchaseOrder | None:
    """Get a single purchase order by ID."""
    for po in _purchase_orders:
        if po.po_id == po_id:
            return po
    return None


def update_po_status(po_id: int, new_status: str) -> PurchaseOrder | None:
    """Update purchase order status (draft -> ready_for_review -> approved/cancelled)."""
    po = get_purchase_order(po_id)
    if po is None:
        return None
    valid = {"draft", "ready_for_review", "approved", "cancelled", "ordered"}
    if new_status not in valid:
        logger.warning("Invalid PO status: %s", new_status)
        return None
    if po.status == "cancelled" and new_status != "cancelled":
        logger.warning("Cannot reactivate cancelled PO #%d", po_id)
        return None
    po.status = new_status
    logger.info("PO #%d status updated to %s", po_id, new_status)
    return po


def _has_recent_order(part_id: str) -> bool:
    """Check if part has an active/recent order in the last 24h."""
    cutoff = datetime.now(UTC) - timedelta(hours=24)
    for po in _purchase_orders:
        if po.part_id != part_id:
            continue
        if po.status in ("cancelled",):
            continue
        try:
            created = datetime.fromisoformat(po.created_at)
            if created > cutoff:
                return True
        except (ValueError, TypeError):
            pass
    return False


def _find_part(part_id: str) -> dict | None:
    if not CATALOG_PATH.exists():
        return None
    with open(CATALOG_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("part_id", "") == part_id:
                return row
    return None


def _find_primary_supplier(part_id: str) -> dict | None:
    """Find primary supplier for the given part using part_suppliers mapping."""
    if not PART_SUPPLIERS_PATH.exists():
        return None
    supplier_id: str | None = None
    with open(PART_SUPPLIERS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("part_id", "") == part_id and row.get("is_primary", "").lower() == "true":
                supplier_id = row.get("supplier_id", "")
                break
    if not supplier_id:
        return None
    with open(SUPPLIERS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("supplier_id", "") == supplier_id:
                return row
    return None


class DuplicateOrderError(Exception):
    """Raised when a duplicate auto-order is prevented."""
