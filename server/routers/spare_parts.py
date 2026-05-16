"""Spare parts router — handles catalog, inventory, tickets, POs, and crisis management."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from db.client import get_supabase_client
from services.crisis_service import CrisisService

router = APIRouter(prefix="/api/spare-parts", tags=["spare-parts"])


# ── Dependency ─────────────────────────────────────────────────


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
    """Get org-wide crisis overview dashboard."""
    return await service.get_crisis_dashboard(org.org_id)


@router.get("/crisis/{part_id}")
async def get_part_crisis_score(
    part_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    service: CrisisService = Depends(_get_crisis_service),
) -> dict[str, Any]:
    """Calculate and return detailed crisis score for a specific part."""
    try:
        return await service.calculate_crisis_score(org.org_id, part_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ── Catalog ────────────────────────────────────────────────────


@router.get("/catalog")
async def get_catalog(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    criticality: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Get paginated spare parts catalog."""
    query = supabase.table("spare_parts_catalog").select("*").eq("org_id", org.org_id)
    if criticality:
        query = query.eq("criticality", criticality)
    
    result = query.range(offset, offset + limit - 1).execute()
    return {"parts": result.data or [], "count": len(result.data or [])}


@router.get("/catalog/{part_id}")
async def get_part_details(
    part_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Get specific part details."""
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


@router.get("/inventory/{part_id}")
async def get_inventory_history(
    part_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    limit: int = Query(10, le=100),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Get recent inventory snapshots for a part."""
    result = (
        supabase.table("inventory_snapshots")
        .select("*")
        .eq("part_id", part_id)
        .eq("org_id", org.org_id)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return {"history": result.data or []}


# ── Tickets ────────────────────────────────────────────────────


@router.get("/tickets")
async def get_tickets(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    status: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """List org-scoped part tickets."""
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
    """Auto-generate PO from a ticket (Manager/Procurement only)."""
    try:
        po = await service.create_auto_order(org.org_id, ticket_id)
        return {"message": "Purchase order created", "purchase_order": po}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Purchase Orders ────────────────────────────────────────────


@router.get("/purchase-orders")
async def get_purchase_orders(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    status: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """List org-scoped purchase orders."""
    query = supabase.table("purchase_orders").select("*").eq("org_id", org.org_id)
    if status:
        query = query.eq("status", status)
        
    result = query.order("order_date", desc=True).range(offset, offset + limit - 1).execute()
    return {"purchase_orders": result.data or []}


@router.post("/purchase-orders/{po_id}/approve")
async def approve_po(
    po_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.APPROVE_PO)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Approve a purchase order (Manager/Procurement only)."""
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
    """Reject a purchase order."""
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


@router.get("/suppliers")
async def get_suppliers(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """List all org suppliers."""
    # This might require joining with supplier_parts to get org-specific suppliers,
    # or assuming the suppliers table is global but supplier_parts is org-scoped.
    # We will list from supplier_parts for this org
    result = (
        supabase.table("supplier_parts")
        .select("suppliers(*)")
        .eq("org_id", org.org_id)
        .execute()
    )
    
    # Deduplicate
    seen = set()
    suppliers = []
    for row in (result.data or []):
        s = row.get("suppliers")
        if s and s["supplier_id"] not in seen:
            seen.add(s["supplier_id"])
            suppliers.append(s)
            
    return {"suppliers": suppliers}


@router.get("/suppliers/{part_id}/alternatives")
async def get_alternative_suppliers(
    part_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_SPARE_PARTS)),
    service: CrisisService = Depends(_get_crisis_service),
) -> dict[str, Any]:
    """Get alternative suppliers for a part."""
    alternatives = await service.get_alternative_suppliers(org.org_id, part_id)
    return {"alternatives": alternatives}
