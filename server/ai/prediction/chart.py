"""Wear projection chart generation using matplotlib."""

import io
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def generate_wear_projection_chart(
    prediction: dict[str, Any],
) -> bytes | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not installed, skipping chart generation")
        return None

    scenarios = prediction.get("scenarios", {})
    points = prediction.get("projection_points", [])
    threshold = prediction.get("critical_threshold_um", 200)

    if not points:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    timestamps = [datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) for p in points]
    wear_values = [p["wear_um"] for p in points]

    machine_id = prediction.get("machine_id", "Unknown")
    current_wear = prediction.get("current_wear_um", 0)
    hours_to_critical = prediction.get("hours_to_critical", 0)
    confidence = prediction.get("confidence", "unknown")
    trend = prediction.get("trend", "unknown")

    ax.plot(timestamps, wear_values, "b-", linewidth=2, label="Mevcut Hiz (Baseline)")

    ax.axhline(y=threshold, color="r", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.text(
        timestamps[0],
        threshold + 5,
        f"Kritik Esik ({threshold:.0f} µm)",
        color="red",
        fontsize=9,
        verticalalignment="bottom",
    )

    if scenarios:
        for label, color, style, _mult in [
            ("Kotu Senaryo (+%25)", "darkorange", ":", 1.25),
            ("Iyi Senaryo (-%25)", "green", "--", 0.75),
        ]:
            sc = scenarios.get("pessimistic" if "Kotu" in label else "optimistic")
            if sc:
                end_time = datetime.fromisoformat(sc["critical_at"].replace("Z", "+00:00"))
                sc_timestamps = [timestamps[0], end_time]
                sc_wear = [current_wear, threshold]
                ax.plot(
                    sc_timestamps,
                    sc_wear,
                    color=color,
                    linestyle=style,
                    linewidth=1.5,
                    alpha=0.6,
                    label=label,
                )

    ax.fill_between(timestamps, 0, wear_values, alpha=0.1, color="blue")

    ax.set_xlabel("Zaman", fontsize=11)
    ax.set_ylabel("Asinma (µm)", fontsize=11)
    ax.set_title(
        f"{machine_id} — Asinma Projeksiyonu\n"
        f"Kritik Esige Kalan: {hours_to_critical:.1f} saat | "
        f"Trend: {trend} | Guven: {confidence}",
        fontsize=12,
        fontweight="bold",
    )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
