from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnomalyDetail(BaseModel):
    image_id: int
    score: float
    wear_type: str = ""
    wear_value_um: float = 0.0
    set_id: int = 0


class WebhookPayload(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    event: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    machine: str = ""
    anomaly: AnomalyDetail | None = None
    image_url: str = ""
    severity: str = "info"
    message: str = ""


class SparePartsCrisisPayload(BaseModel):
    event: str = "spare_parts_crisis"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    part_id: int
    part_name: str
    on_hand: int = 0
    needed_by: str = ""
    lead_time_days_p90: int = 0
    crisis_score: float = 0.0
    risk_level: str = "none"
    alternative_suppliers: list[dict] = Field(default_factory=list)


class PurchaseOrderPayload(BaseModel):
    event: str = "purchase_order_created"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    po_id: int = 0
    part_name: str = ""
    supplier_name: str = ""
    quantity: int = 0
    unit_price: float = 0.0
    total: float = 0.0
    status: str = "ready_for_review"


class WebhookLog(BaseModel):
    id: int | None = None
    event_type: str
    payload: dict
    webhook_url: str
    status: str
    attempt: int = 1
    error: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class NotificationRequest(BaseModel):
    anomaly_id: int
    score: float
    wear_type: str = ""
    wear_value_um: float = 0.0
    set_id: int = 0
    image_url: str = ""
    machine: str = ""
    message: str = ""


class ReportRequest(BaseModel):
    report_type: str
    parameters: dict = Field(default_factory=dict)


class CrisisScoreResponse(BaseModel):
    image_id: int
    crisis_score: float
    risk_level: str
    breakdown: dict


class AutoOrderRequest(BaseModel):
    part_id: int
    quantity: int = 1
    trigger: str = "crisis"
