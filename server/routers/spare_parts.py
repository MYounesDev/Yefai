"""Spare parts router — Phase 3B.

Crisis score, auto-order, alternative supplier, and inventory endpoints.
"""

import csv
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ai.puqai.schemas import AutoOrderRequest, CrisisScoreResponse
from services.crisis_service import calculate_crisis_score
from services.purchase_order_service import (
    DuplicateOrderError,
    PurchaseOrder,
    create_auto_order,
    get_purchase_order,
    get_purchase_orders,
    update_po_status,
)
from services.supplier_service import find_alternatives

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/spare-parts", tags=["spare-parts"])

_MOCK_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mock"
CATALOG_PATH = _MOCK_DIR / "spare_parts_catalog.csv"
INVENTORY_PATH = _MOCK_DIR / "inventory_snapshots.csv"


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@router.get("/catalog")
async def get_catalog(
    criticality: str | None = Query(None, description="Filter by criticality (A/B/C)"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> dict[str, Any]:
    """Get spare parts catalog with optional criticality filter."""
    rows = _load_csv(CATALOG_PATH)
    if criticality:
        rows = [r for r in rows if r.get("criticality", "").upper() == criticality.upper()]
    return {"items": rows[:limit], "count": min(len(rows), limit), "total": len(rows)}


@router.get("/crisis-score/{image_id}", response_model=CrisisScoreResponse)
async def get_crisis_score(
    image_id: int,
    anomaly_score: float = Query(0.5, ge=0.0, le=1.0, description="Anomaly detection score"),
) -> CrisisScoreResponse:
    """Calculate crisis score for an image/anomaly."""
    try:
        result = calculate_crisis_score(image_id, anomaly_score)
        if result.risk_level == "none" and result.crisis_score == 0.0 and result.part_id == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No related part found for image_id={image_id}",
            )
        return CrisisScoreResponse(
            image_id=result.image_id,
            crisis_score=result.crisis_score,
            risk_level=result.risk_level,
            breakdown=result.breakdown or {},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to calculate crisis score")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/auto-order")
async def auto_order(
    request: AutoOrderRequest,
) -> dict[str, Any]:
    """Automatically create a purchase order for a part.

    Duplicate orders for the same part within 24h are prevented.
    Crisis/at-risk level parts automatically get orders.
    """
    try:
        po = create_auto_order(
            part_id=str(request.part_id),
            quantity=request.quantity,
            trigger=request.trigger,
        )
        return {"po": _po_to_dict(po), "created": True}
    except DuplicateOrderError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to create auto order")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/alternative-suppliers/{part_id}")
async def get_alternative_suppliers(
    part_id: str,
    max_lead_time_days: int = Query(
        0, ge=0, description="Max acceptable lead time in days (0=no filter)"
    ),
) -> dict[str, Any]:
    """Find alternative suppliers for a part.

    Returns ranked alternatives with lead time, cost delta, and reliability comparison.
    """
    try:
        result = find_alternatives(part_id, max_lead_time_days=max_lead_time_days)
        return {
            "part_id": result.part_id,
            "part_name": result.part_name,
            "primary": _supplier_to_dict(result.primary) if result.primary else None,
            "alternatives": [_supplier_to_dict(a) for a in result.alternatives],
            "total_alternatives": len(result.alternatives),
            "warning": result.no_alternative_warning,
        }
    except Exception as e:
        logger.exception("Failed to find alternative suppliers")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/inventory")
async def get_inventory(
    part_id: str | None = Query(None, description="Filter by part ID"),
    low_stock: bool = Query(False, description="Only show items below min_level"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> dict[str, Any]:
    """Get inventory snapshot."""
    rows = _load_csv(INVENTORY_PATH)
    if part_id:
        rows = [r for r in rows if r.get("part_id", "") == part_id]
    if low_stock:
        rows = [r for r in rows if int(r.get("on_hand", 0)) < int(r.get("min_level", 10))]
    return {"items": rows[:limit], "count": min(len(rows), limit), "total": len(rows)}


@router.get("/purchase-orders")
async def list_purchase_orders(
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> dict[str, Any]:
    """List purchase orders with optional status filter."""
    try:
        orders = get_purchase_orders(status=status, limit=limit)
        return {
            "orders": [_po_to_dict(po) for po in orders],
            "count": len(orders),
        }
    except Exception as e:
        logger.exception("Failed to list purchase orders")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/purchase-orders/{po_id}")
async def get_po(po_id: int) -> dict[str, Any]:
    """Get a single purchase order by ID."""
    po = get_purchase_order(po_id)
    if po is None:
        raise HTTPException(status_code=404, detail=f"Purchase order #{po_id} not found")
    return {"po": _po_to_dict(po)}


@router.patch("/purchase-orders/{po_id}/status")
async def change_po_status(
    po_id: int,
    status: str = Query(..., description="New status (approved/cancelled)"),
) -> dict[str, Any]:
    """Update purchase order status (e.g., approve or cancel)."""
    try:
        updated = update_po_status(po_id, status)
        if updated is None:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update PO #{po_id} to status={status}",
            )
        return {"po": _po_to_dict(updated), "status_updated": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update PO status")
        raise HTTPException(status_code=500, detail=str(e)) from e


def _po_to_dict(po: PurchaseOrder) -> dict[str, Any]:
    return {
        "po_id": po.po_id,
        "part_id": po.part_id,
        "part_name": po.part_name,
        "supplier_id": po.supplier_id,
        "supplier_name": po.supplier_name,
        "quantity": po.quantity,
        "unit_price": po.unit_price,
        "total": po.total,
        "lead_time_days": po.lead_time_days,
        "status": po.status,
        "created_at": po.created_at,
        "trigger": po.trigger,
    }


def _supplier_to_dict(s) -> dict[str, Any]:
    return {
        "supplier_id": s.supplier_id,
        "supplier_name": s.supplier_name,
        "lead_time_p90": s.lead_time_p90,
        "reliability_score": s.reliability_score,
        "cost_delta_pct": s.cost_delta_pct,
        "overall_score": s.overall_score,
        "is_primary": s.is_primary,
        "is_viable": s.is_viable,
    }
