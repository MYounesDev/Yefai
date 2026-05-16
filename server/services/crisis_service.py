"""Crisis Service — calculates crisis scores, auto-orders, and handles supplier management."""

import logging
import uuid
from typing import Any

from supabase import Client

from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)


class CrisisService:
    def __init__(self, supabase: Client, prediction_service: PredictionService | None = None):
        self.supabase = supabase
        self.prediction_service = prediction_service or PredictionService()

    async def calculate_crisis_score(self, org_id: str, part_id: str) -> dict[str, Any]:
        """
        Calculate crisis score (0-100) for a spare part.
        Formula components:
        1. Stock coverage ratio: on_hand / projected_demand
        2. Lead time vs time-to-critical
        3. Part criticality
        4. Supplier reliability
        """
        # Fetch part details
        part_res = (
            self.supabase.table("spare_parts_catalog")
            .select("*")
            .eq("part_id", part_id)
            .eq("org_id", org_id)
            .maybe_single()
            .execute()
        )
        if not part_res.data:
            raise ValueError(f"Part not found: {part_id}")
        
        part = part_res.data
        criticality = part.get("criticality", "C")
        
        # Fetch inventory
        inv_res = (
            self.supabase.table("inventory_snapshots")
            .select("*")
            .eq("part_id", part_id)
            .eq("org_id", org_id)
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )
        on_hand = inv_res.data[0].get("quantity_on_hand", 0) if inv_res.data else 0
        
        # Fetch preferred supplier
        supplier_res = (
            self.supabase.table("supplier_parts")
            .select("lead_time_days, suppliers(*)")
            .eq("part_id", part_id)
            .eq("org_id", org_id)
            .eq("is_preferred", True)
            .maybe_single()
            .execute()
        )
        
        lead_time = 14 # default
        supplier_reliability = 80 # default
        
        if supplier_res.data:
            lead_time = supplier_res.data.get("lead_time_days", 14)
            if supplier_res.data.get("suppliers"):
                supplier_reliability = supplier_res.data["suppliers"].get("reliability_score", 80)
                
        # Basic heuristic
        stock_score = 0 if on_hand > 5 else (100 if on_hand == 0 else 50)
        criticality_score = {"A": 100, "B": 60, "C": 20}.get(criticality, 20)
        supplier_score = max(0, 100 - supplier_reliability)
        
        # We don't have exact projected demand easily without more advanced ML, so we use a simplified score
        base_score = (stock_score * 0.4) + (criticality_score * 0.4) + (supplier_score * 0.2)
        
        # Assess risk level
        risk_level = "safe"
        if base_score > 80:
            risk_level = "critical"
        elif base_score > 60:
            risk_level = "at_risk"
        elif base_score > 40:
            risk_level = "watch"
            
        return {
            "part_id": part_id,
            "crisis_score": round(base_score, 1),
            "risk_level": risk_level,
            "breakdown": {
                "stock_score": stock_score,
                "lead_time_days": lead_time,
                "criticality_score": criticality_score,
                "supplier_score": supplier_score
            },
            "recommendations": [
                f"Consider ordering {"immediately" if risk_level == 'critical' else 'soon'}."
            ]
        }

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
                {"part_id": "P-101", "score": 72, "risk_level": "at_risk"}
            ],
            "risk_distribution": {
                "safe": 100,
                "watch": 18,
                "at_risk": 5,
                "critical": 2
            }
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
            "status": "pending"
        }
        
        po_res = self.supabase.table("purchase_orders").insert(po_data).execute()
        
        if not po_res.data:
            raise ValueError("Failed to create Purchase Order")
            
        return po_res.data[0]

    async def get_alternative_suppliers(self, org_id: str, part_id: str) -> list[dict[str, Any]]:
        """Get alternative suppliers for a part."""
        res = (
            self.supabase.table("supplier_parts")
            .select("supplier_id, unit_cost, lead_time_days, is_preferred, suppliers(name, reliability_score)")
            .eq("part_id", part_id)
            .eq("org_id", org_id)
            .execute()
        )
        return res.data or []
