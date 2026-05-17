"""Spare parts router — Phase 3B (Merged)

Handles catalog, inventory, tickets, POs, and crisis management,
incorporating both mock CSV systems and Supabase integrations.
"""

import csv
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

# Main file imports
from ai.puqai.schemas import AutoOrderRequest, CrisisScoreResponse

# ABC file imports
from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from db.client import get_supabase_client
from services.crisis_service import CrisisService, calculate_crisis_score
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

# ── Constants & Utilities (From Main) ──────────────────────────

_MOCK_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mock"
CATALOG_PATH = _MOCK_DIR / "spare_parts_catalog.csv"
INVENTORY_PATH = _MOCK_DIR / "inventory_snapshots.csv"


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


# ── Dependencies (From ABC) ────────────────────────────────────


def _get_crisis_service(supabase: Client = Depends(get_supabase_client)) -> CrisisService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return CrisisService(supabase)


# ── Crisis Dashboard ───────────────────────────────────────────


@router.get("/crisis")
async def get_crisis_dashboard(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    service: CrisisService = Depends(_get_crisis_service),
) -> dict[str, Any]:
    """Get org-wide crisis overview dashboard (From ABC)."""
    return await service.get_crisis_dashboard(org.org_id)


@router.get("/crisis-score/{image_id}", response_model=CrisisScoreResponse)
async def get_crisis_score(
    image_id: int,
    anomaly_score: float = Query(0.5, ge=0.0, le=1.0, description="Anomaly detection score"),
) -> CrisisScoreResponse:
    """Calculate crisis score for an image/anomaly (From Main)."""
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


@router.get("/crisis/{part_id}")
async def get_part_crisis_score(
    part_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    service: CrisisService = Depends(_get_crisis_service),
) -> dict[str, Any]:
    """Calculate and return detailed crisis score for a specific part (From ABC)."""
    try:
        return await service.calculate_crisis_score(org.org_id, part_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ── Catalog ────────────────────────────────────────────────────


@router.get("/catalog")
async def get_catalog(
    criticality: str | None = Query(None, description="Filter by criticality (A/B/C)"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> dict[str, Any]:
    """Get spare parts catalog with optional criticality filter (From Main)."""
    rows = _load_csv(CATALOG_PATH)
    if criticality:
        rows = [r for r in rows if r.get("criticality", "").upper() == criticality.upper()]
    return {"items": rows[:limit], "count": min(len(rows), limit), "total": len(rows)}


@router.get("/catalog/{part_id}")
async def get_part_details(
    part_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Get specific part details (From ABC)."""
    result = (
        supabase.table("spare_parts_catalog")
        .select("*")
        .eq("part_id", part_id)
        .eq("org_id", org.org_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Part not found")
    return result.data


# ── Inventory ──────────────────────────────────────────────────


@router.get("/inventory")
async def get_inventory(
    part_id: str | None = Query(None, description="Filter by part ID"),
    low_stock: bool = Query(False, description="Only show items below min_level"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> dict[str, Any]:
    """Get inventory snapshot (From Main)."""
    rows = _load_csv(INVENTORY_PATH)
    if part_id:
        rows = [r for r in rows if r.get("part_id", "") == part_id]
    if low_stock:
        rows = [r for r in rows if int(r.get("on_hand", 0)) < int(r.get("min_level", 10))]
    return {"items": rows[:limit], "count": min(len(rows), limit), "total": len(rows)}


@router.get("/inventory/{part_id}")
async def get_inventory_history(
    part_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    limit: int = Query(10, le=100),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Get recent inventory snapshots for a part (From ABC)."""
    result = (
        supabase.table("inventory_snapshots")
        .select("*")
        .eq("part_id", part_id)
        .eq("org_id", org.org_id)
        .order("snapshot_date", desc=True)
        .limit(limit)
        .execute()
    )
    return {"history": result.data or []}


# ── Tickets & Auto-Order ───────────────────────────────────────


@router.post("/auto-order")
async def auto_order(
    request: AutoOrderRequest,
) -> dict[str, Any]:
    """Automatically create a purchase order for a part (From Main).

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


@router.get("/tickets")
async def get_tickets(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    status: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """List org-scoped part tickets (From ABC)."""
    query = supabase.table("part_tickets").select("*").eq("org_id", org.org_id)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return {"tickets": result.data or []}


@router.post("/tickets/{ticket_id}/auto-order")
async def auto_order_ticket(
    ticket_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.APPROVE_PO)),
    service: CrisisService = Depends(_get_crisis_service),
) -> dict[str, Any]:
    """Auto-generate PO from a ticket (Manager/Procurement only) (From ABC)."""
    try:
        po = await service.create_auto_order(org.org_id, ticket_id)
        return {"message": "Purchase order created", "purchase_order": po}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Purchase Orders ────────────────────────────────────────────


@router.get("/purchase-orders")
async def list_purchase_orders(
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> dict[str, Any]:
    """List purchase orders with optional status filter (From Main)."""
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
    """Get a single purchase order by ID (From Main)."""
    po = get_purchase_order(po_id)
    if po is None:
        raise HTTPException(status_code=404, detail=f"Purchase order #{po_id} not found")
    return {"po": _po_to_dict(po)}


@router.patch("/purchase-orders/{po_id}/status")
async def change_po_status(
    po_id: int,
    status: str = Query(..., description="New status (approved/cancelled)"),
) -> dict[str, Any]:
    """Update purchase order status (e.g., approve or cancel) (From Main)."""
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


@router.post("/purchase-orders/{po_id}/approve")
async def approve_po(
    po_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.APPROVE_PO)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Approve a purchase order in supabase (Manager/Procurement only) (From ABC)."""
    result = (
        supabase.table("purchase_orders")
        .update({"status": "approved"})
        .eq("po_id", po_id)
        .eq("org_id", org.org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return {"message": "Purchase order approved", "purchase_order": result.data[0]}


@router.post("/purchase-orders/{po_id}/reject")
async def reject_po(
    po_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.APPROVE_PO)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Reject a purchase order in supabase (From ABC)."""
    result = (
        supabase.table("purchase_orders")
        .update({"status": "rejected"})
        .eq("po_id", po_id)
        .eq("org_id", org.org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return {"message": "Purchase order rejected", "purchase_order": result.data[0]}


# ── Suppliers ──────────────────────────────────────────────────


@router.get("/alternative-suppliers/{part_id}")
async def get_alternative_suppliers(
    part_id: str,
    max_lead_time_days: int = Query(
        0, ge=0, description="Max acceptable lead time in days (0=no filter)"
    ),
) -> dict[str, Any]:
    """Find alternative suppliers for a part (From Main).

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


@router.get("/suppliers")
async def get_suppliers(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """List all org suppliers (From ABC)."""
    result = (
        supabase.table("supplier_parts").select("suppliers(*)").eq("org_id", org.org_id).execute()
    )

    seen = set()
    suppliers = []
    for row in result.data or []:
        s = row.get("suppliers")
        if s and s["supplier_id"] not in seen:
            seen.add(s["supplier_id"])
            suppliers.append(s)

    return {"suppliers": suppliers}
