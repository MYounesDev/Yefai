from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)


def render_template(name: str, **kwargs: object) -> str:
    try:
        tmpl = _env.get_template(name)
    except Exception:
        return ""
    return tmpl.render(**kwargs)


def render_telegram_anomaly(
    machine: str,
    anomaly_id: int,
    score: float,
    wear_type: str,
    wear_value_um: float,
    image_url: str,
) -> str:
    return render_template(
        "telegram_anomaly.j2",
        machine=machine,
        anomaly_id=anomaly_id,
        score=score,
        wear_type=wear_type or "unknown",
        wear_value_um=f"{wear_value_um:.1f}",
        image_url=image_url,
    )


def render_email_report(
    machine: str,
    anomaly_id: int,
    score: float,
    wear_type: str,
    wear_value_um: float,
    set_id: int,
    image_url: str,
    timestamp: str,
) -> str:
    return render_template(
        "email_report.j2",
        machine=machine,
        anomaly_id=anomaly_id,
        score=score,
        wear_type=wear_type or "unknown",
        wear_value_um=f"{wear_value_um:.1f}",
        set_id=set_id,
        image_url=image_url,
        timestamp=timestamp,
    )


def render_sms_critical(
    machine: str,
    wear_type: str,
    wear_value_um: float,
    set_id: int,
) -> str:
    return render_template(
        "sms_critical.j2",
        machine=machine,
        wear_type=wear_type or "unknown",
        wear_value_um=f"{wear_value_um:.0f}",
        set_id=set_id,
    )


def render_crisis_payload(
    part_name: str,
    on_hand: int,
    crisis_score: float,
    risk_level: str,
    lead_time_days: int,
    alt_suppliers: str,
) -> str:
    return render_template(
        "spare_parts_crisis.j2",
        part_name=part_name,
        on_hand=on_hand,
        crisis_score=crisis_score,
        risk_level=risk_level,
        lead_time_days=lead_time_days,
        alt_suppliers=alt_suppliers,
    )


def render_po_payload(
    part_name: str,
    supplier_name: str,
    quantity: int,
    unit_price: float,
    total: float,
    po_id: int,
) -> str:
    return render_template(
        "po_notification.j2",
        part_name=part_name,
        supplier_name=supplier_name,
        quantity=quantity,
        unit_price=f"{unit_price:.2f}",
        total=f"{total:.2f}",
        po_id=po_id,
    )
