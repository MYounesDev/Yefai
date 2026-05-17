"""Spare-parts crisis workflow orchestration for mock-mode demos."""

import logging
import math
from datetime import UTC, datetime, timedelta
from typing import Any

from supabase import Client

from ai.puqai.schemas import (
    CrisisWorkflowRequest,
    PurchaseOrderPayload,
    SparePartsCrisisPayload,
)
from services.crisis_service import CrisisResult, calculate_crisis_score
from services.notification_service import NotificationService
from services.prediction_service import PredictionService
from services.purchase_order_service import DuplicateOrderError, PurchaseOrder, create_auto_order
from services.supplier_service import AlternativeResult, SupplierComparison, find_alternatives

logger = logging.getLogger(__name__)


class SparePartsWorkflowService:
    """Runs prediction → crisis score → PO → supplier → notification workflow."""

    def __init__(
        self,
        supabase: Client | None = None,
        notification_service: NotificationService | None = None,
    ) -> None:
        self.supabase = supabase
        self.notification_service = notification_service or NotificationService(supabase)

    async def run(self, request: CrisisWorkflowRequest) -> dict[str, Any]:
        prediction = await self._get_prediction(request)
        hours_to_critical = _float_or_none(prediction.get("hours_to_critical"))

        crisis = calculate_crisis_score(
            image_id=request.image_id,
            anomaly_score=request.anomaly_score,
            hours_to_critical=hours_to_critical,
        )
        if crisis.part_id == 0 and crisis.crisis_score == 0.0:
            raise ValueError(f"No related part found for image_id={request.image_id}")

        max_lead_time_days = _hours_to_days(hours_to_critical)
        suppliers = find_alternatives(str(crisis.part_id), max_lead_time_days=max_lead_time_days)

        po = self._maybe_create_purchase_order(request, crisis)
        needed_by = _needed_by_iso(hours_to_critical)
        notification = await self._maybe_notify(request, crisis, suppliers, po.get("po"), needed_by)

        return {
            "image_id": request.image_id,
            "machine_id": request.machine_id,
            "prediction": prediction,
            "crisis": _crisis_to_dict(crisis, needed_by),
            "purchase_order": po,
            "alternative_suppliers": [_supplier_to_dict(s) for s in suppliers.alternatives],
            "notification": notification,
        }

    async def _get_prediction(self, request: CrisisWorkflowRequest) -> dict[str, Any]:
        if self.supabase is not None:
            try:
                prediction = await PredictionService(self.supabase).get_prediction(
                    request.machine_id
                )
                if "error" not in prediction:
                    return prediction
            except Exception as exc:
                logger.warning(
                    "Prediction lookup failed for machine_id=%s; using mock fallback: %s",
                    request.machine_id,
                    exc,
                )

        hours_to_critical = request.hours_to_critical
        if hours_to_critical is None:
            hours_to_critical = max(1.0, round((1.0 - request.anomaly_score) * 96.0, 1))

        return {
            "machine_id": request.machine_id,
            "current_wear_um": round(request.anomaly_score * 200.0, 1),
            "critical_threshold_um": 200.0,
            "wear_rate_um_per_hour": 0.0,
            "hours_to_critical": hours_to_critical,
            "confidence": "mock_fallback",
            "trend": "accelerating" if request.anomaly_score >= 0.8 else "stable",
            "scenarios": {},
            "projection_points": [],
            "last_check_at": datetime.now(UTC).isoformat(),
            "status": "red" if hours_to_critical <= 24 else "yellow",
            "source": "mock_fallback",
        }

    def _maybe_create_purchase_order(
        self,
        request: CrisisWorkflowRequest,
        crisis: CrisisResult,
    ) -> dict[str, Any]:
        if not request.auto_order:
            return {"created": False, "reason": "auto_order_disabled", "po": None}
        if not crisis.needs_auto_order:
            return {"created": False, "reason": f"risk_level_{crisis.risk_level}", "po": None}

        try:
            po = create_auto_order(
                part_id=str(crisis.part_id),
                quantity=request.quantity,
                trigger=crisis.risk_level,
            )
            return {"created": True, "po": _po_to_dict(po)}
        except DuplicateOrderError as exc:
            return {
                "created": False,
                "reason": "duplicate_order_prevented",
                "detail": str(exc),
                "po": None,
            }

    async def _maybe_notify(
        self,
        request: CrisisWorkflowRequest,
        crisis: CrisisResult,
        suppliers: AlternativeResult,
        po: dict[str, Any] | None,
        needed_by: str,
    ) -> dict[str, Any]:
        if not request.notify:
            return {"sent": False, "reason": "notify_disabled", "logs": []}
        if crisis.risk_level == "none":
            return {"sent": False, "reason": "risk_level_none", "logs": []}

        crisis_payload = SparePartsCrisisPayload(
            part_id=crisis.part_id,
            part_name=crisis.part_name,
            on_hand=int((crisis.breakdown or {}).get("on_hand", 0)),
            needed_by=needed_by,
            lead_time_days_p90=int((crisis.breakdown or {}).get("lead_time_p90_days", 0)),
            crisis_score=crisis.crisis_score,
            risk_level=crisis.risk_level,
            alternative_suppliers=[_supplier_to_dict(s) for s in suppliers.alternatives],
        )
        po_payload = _po_payload(po) if po else None
        logs = await self.notification_service.send_spare_parts_crisis(crisis_payload, po_payload)
        return {"sent": True, "logs": [log.model_dump() for log in logs]}


def _hours_to_days(hours: float | None) -> int:
    if hours is None:
        return 0
    return max(1, math.ceil(hours / 24.0))


def _needed_by_iso(hours: float | None) -> str:
    delta = timedelta(hours=hours if hours is not None else 0.0)
    return (datetime.now(UTC) + delta).isoformat()


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _crisis_to_dict(crisis: CrisisResult, needed_by: str) -> dict[str, Any]:
    return {
        "part_id": crisis.part_id,
        "part_name": crisis.part_name,
        "crisis_score": crisis.crisis_score,
        "risk_level": crisis.risk_level,
        "needed_by": needed_by,
        "needs_auto_order": crisis.needs_auto_order,
        "breakdown": crisis.breakdown or {},
    }


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


def _supplier_to_dict(supplier: SupplierComparison) -> dict[str, Any]:
    return {
        "supplier_id": supplier.supplier_id,
        "supplier_name": supplier.supplier_name,
        "lead_time_p90": supplier.lead_time_p90,
        "reliability_score": supplier.reliability_score,
        "cost_delta_pct": supplier.cost_delta_pct,
        "overall_score": supplier.overall_score,
        "is_primary": supplier.is_primary,
        "is_viable": supplier.is_viable,
    }


def _po_payload(po: dict[str, Any]) -> PurchaseOrderPayload:
    return PurchaseOrderPayload(
        po_id=int(po.get("po_id", 0)),
        part_name=str(po.get("part_name", "")),
        supplier_name=str(po.get("supplier_name", "")),
        quantity=int(po.get("quantity", 0)),
        unit_price=float(po.get("unit_price", 0.0)),
        total=float(po.get("total", 0.0)),
        status=str(po.get("status", "ready_for_review")),
    )
