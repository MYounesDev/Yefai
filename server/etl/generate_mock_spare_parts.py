import argparse
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

np.random.seed(42)

NUM_PARTS = 40
NUM_SUPPLIERS = 10

CRITICALITY_WEIGHTS = {"A": 0.15, "B": 0.35, "C": 0.50}
DEMAND_PATTERN_WEIGHTS = {"intermittent": 0.45, "erratic": 0.25, "lumpy": 0.20, "smooth": 0.10}

PARTS_POOL = [
    ("INSERT_CARBIDE_DCMT", "Carbide Insert DCMT 11T304"),
    ("INSERT_CBN_RNGN", "CBN Insert RNGN 120400"),
    ("TOOLHOLDER_PCLNR", "Tool Holder PCLNR 2525M12"),
    ("TOOLHOLDER_SVJCR", "Tool Holder SVJCR 2525M16"),
    ("ENDMILL_10MM", "Solid Carbide End Mill 10mm"),
    ("ENDMILL_12MM", "Solid Carbide End Mill 12mm"),
    ("DRILL_8MM", "Carbide Drill 8mm"),
    ("DRILL_10MM", "Carbide Drill 10mm"),
    ("TAP_M8", "Spiral Tap M8x1.25"),
    ("TAP_M10", "Spiral Tap M10x1.5"),
    ("REAMER_12H7", "Machine Reamer 12H7"),
    ("REAMER_16H7", "Machine Reamer 16H7"),
    ("COLLET_ER32_10", "ER32 Collet 10mm"),
    ("COLLET_ER32_12", "ER32 Collet 12mm"),
    ("PULL_STUD_M16", "Pull Stud M16"),
    ("VISE_JAW_SOFT", "Soft Jaw Set Vise 150mm"),
    ("COOLANT_NOZZLE", "Flexible Coolant Nozzle"),
    ("CHIP_CONVEYOR_BELT", "Chip Conveyor Belt"),
    ("SPINDLE_BELT", "Spindle Drive Belt"),
    ("BALL_SCREW_X", "Ball Screw X-Axis"),
    ("BALL_SCREW_Z", "Ball Screw Z-Axis"),
    ("LINEAR_GUIDE_25MM", "Linear Guide Rail 25mm"),
    ("LINEAR_GUIDE_35MM", "Linear Guide Rail 35mm"),
    ("SEAL_KIT_SPINDLE", "Spindle Seal Kit"),
    ("HYDRAULIC_HOSE", "Hydraulic Hose Assembly"),
    ("OIL_FILTER", "Hydraulic Oil Filter Element"),
    ("WAY_WIPER", "Way Wiper Set"),
    ("PROXIMITY_SENSOR", "Inductive Proximity Sensor M12"),
    ("PRESSURE_SWITCH", "Hydraulic Pressure Switch"),
    ("DRIVE_BELT_SERVO", "Servo Motor Drive Belt"),
    ("COUPLING_SERVO", "Servo Motor Coupling"),
    ("BEARING_SK_6205", "Deep Groove Ball Bearing 6205"),
    ("BEARING_SK_7206", "Angular Contact Bearing 7206"),
    ("O_RING_KIT", "O-Ring Seal Kit NBR"),
    ("FILTER_AIR", "Air Filter Element"),
    ("CHUCK_JAWS", "Hydraulic Chuck Jaw Set"),
    ("COOLANT_PUMP_SEAL", "Coolant Pump Mechanical Seal"),
    ("TOOL_PRESETTER_STYLUS", "Tool Presetter Stylus Tip"),
    ("WORK_LAMP_LED", "LED Work Lamp IP67"),
    ("POWER_SUPPLY_24V", "24VDC Power Supply 10A"),
]

SUPPLIER_NAMES = [
    ("SANDVIK", "Sandvik Coromant"),
    ("KENNAMETAL", "Kennametal GmbH"),
    ("ISCAR_TR", "Iscar Turkey"),
    ("MITS_CARB", "Mitsubishi Materials"),
    ("HAAS_PARTS", "Haas Factory Outlet"),
    ("DMGMORI_SP", "DMG MORI Spare Parts"),
    ("BOSCH_REX", "Bosch Rexroth"),
    ("SKF_DIST", "SKF Distributor"),
    ("LOCAL_TED", "Local Tedarikci A.S."),
    ("FAST_SUPP", "Fast Supply Ltd."),
]


def generate_catalog(num_parts: int = NUM_PARTS) -> pd.DataFrame:
    records = []
    for i in range(num_parts):
        p_id, p_name = PARTS_POOL[i % len(PARTS_POOL)]
        crit = np.random.choice(
            list(CRITICALITY_WEIGHTS.keys()),
            p=list(CRITICALITY_WEIGHTS.values()),
        )
        demand = np.random.choice(
            list(DEMAND_PATTERN_WEIGHTS.keys()),
            p=list(DEMAND_PATTERN_WEIGHTS.values()),
        )

        if crit == "A":
            cost = np.random.uniform(200, 3000)
            lt_p50 = np.random.randint(14, 45)
        elif crit == "B":
            cost = np.random.uniform(50, 800)
            lt_p50 = np.random.randint(7, 21)
        else:
            cost = np.random.uniform(5, 150)
            lt_p50 = np.random.randint(1, 10)

        lt_p90 = int(lt_p50 * np.random.uniform(1.3, 2.5))

        records.append(
            {
                "part_id": f"{p_id}_{i:02d}",
                "part_name": p_name,
                "criticality": crit,
                "demand_pattern": demand,
                "unit_cost": round(cost, 2),
                "lead_time_p50": lt_p50,
                "lead_time_p90": lt_p90,
                "min_stock": np.random.randint(0, 5),
                "max_stock": np.random.randint(5, 30),
            }
        )

    df = pd.DataFrame(records)
    logger.info("Generated %d spare parts catalog entries", len(df))
    return df


def generate_suppliers(num_suppliers: int = NUM_SUPPLIERS) -> pd.DataFrame:
    records = []
    for i in range(num_suppliers):
        s_id, s_name = SUPPLIER_NAMES[i]
        reliability = round(np.random.uniform(0.6, 0.98), 2)
        lt_p50 = np.random.randint(1, 21)
        lt_p90 = int(lt_p50 * np.random.uniform(1.2, 3.0))

        records.append(
            {
                "supplier_id": s_id,
                "supplier_name": s_name,
                "reliability_score": reliability,
                "lead_time_p50": lt_p50,
                "lead_time_p90": lt_p90,
                "is_primary": i < 5,
            }
        )

    df = pd.DataFrame(records)
    logger.info("Generated %d supplier entries", len(df))
    return df


def generate_inventory(catalog: pd.DataFrame) -> pd.DataFrame:
    records = []
    now = datetime.now(UTC)

    for _, part in catalog.iterrows():
        max_level = part["max_stock"]
        min_level = part["min_stock"]

        if part["criticality"] == "A":
            on_hand = np.random.choice([0, 0, 1, 2], p=[0.25, 0.15, 0.35, 0.25])
        elif part["criticality"] == "B":
            on_hand = np.random.randint(0, max(2, max_level // 2))
        else:
            on_hand = np.random.randint(min_level, max_level + 1)

        on_order = 0
        if on_hand < min_level:
            on_order = np.random.randint(1, 4)

        records.append(
            {
                "part_id": part["part_id"],
                "on_hand": int(on_hand),
                "on_order": int(on_order),
                "min_level": int(min_level),
                "max_level": int(max_level),
                "snapshot_date": now.isoformat(),
            }
        )

    df = pd.DataFrame(records)
    logger.info("Generated %d inventory snapshots", len(df))
    return df


def compute_crisis_score(
    on_hand: int,
    min_level: int,
    lead_time_p90: int,
    criticality: str,
    reliability: float,
) -> float:
    stock_gap = max(0, (min_level - on_hand) / max(min_level, 1))
    crit_map = {"A": 1.0, "B": 0.6, "C": 0.3}
    lt_factor = min(1.0, lead_time_p90 / 30.0)

    score = (
        40 * stock_gap
        + 30 * crit_map.get(criticality, 0.3)
        + 20 * lt_factor
        + 10 * (1.0 - reliability)
    )

    if on_hand == 0:
        score = min(100, score + 15)

    return round(min(100, score), 1)


def risk_level(score: float) -> str:
    if score > 70:
        return "crisis"
    elif score > 40:
        return "at_risk"
    elif score > 10:
        return "watch"
    return "none"


def generate_tickets_and_pos(
    catalog: pd.DataFrame,
    inventory: pd.DataFrame,
    suppliers: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    tickets = []
    pos = []
    now = datetime.now(UTC)
    inv_map = {r["part_id"]: r for _, r in inventory.iterrows()}

    for _, part in catalog.iterrows():
        pid = part["part_id"]
        inv = inv_map.get(pid)
        if inv is None:
            continue

        primary_supp = suppliers[suppliers["is_primary"]].sample(1).iloc[0]
        score = compute_crisis_score(
            inv["on_hand"],
            inv["min_level"],
            part["lead_time_p90"],
            part["criticality"],
            primary_supp["reliability_score"],
        )
        risk = risk_level(score)

        ticket_status = "waiting_part"
        if risk in ("crisis", "at_risk"):
            ticket_status = "stockout"

        tickets.append(
            {
                "part_id": pid,
                "status": ticket_status,
                "quantity": np.random.randint(1, 4),
                "needed_by": (now + timedelta(days=np.random.randint(1, 10))).isoformat(),
                "crisis_score": score,
                "risk": risk,
                "created_at": now.isoformat(),
            }
        )

        if risk in ("crisis", "at_risk"):
            po_status = "ready_for_review"
            po = {
                "part_id": pid,
                "supplier_id": primary_supp["supplier_id"],
                "quantity": inv["min_level"] - inv["on_hand"] + 2,
                "status": po_status,
                "crisis_score": score,
                "risk": risk,
                "created_at": now.isoformat(),
            }
            pos.append(po)

    tickets_df = pd.DataFrame(tickets)
    pos_df = (
        pd.DataFrame(pos)
        if pos
        else pd.DataFrame(
            columns=[
                "part_id",
                "supplier_id",
                "quantity",
                "status",
                "crisis_score",
                "risk",
                "created_at",
            ]
        )
    )

    n_crisis = len(tickets_df[tickets_df["risk"] == "crisis"])
    n_at_risk = len(tickets_df[tickets_df["risk"] == "at_risk"])
    logger.info(
        "Generated %d ticket(s) — %d crisis, %d at_risk", len(tickets_df), n_crisis, n_at_risk
    )
    logger.info("Generated %d purchase order(s)", len(pos_df))
    return tickets_df, pos_df


def export_all(output_dir: Path, **dfs: pd.DataFrame) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, df in dfs.items():
        path = output_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        logger.info("Exported %s (%d rows)", path, len(df))


def generate_all(output_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    if output_dir is None:
        script_dir = Path(__file__).resolve().parent
        output_dir = script_dir.parent.parent / "data" / "mock"

    catalog = generate_catalog()
    suppliers_df = generate_suppliers()
    inventory = generate_inventory(catalog)
    tickets, pos = generate_tickets_and_pos(catalog, inventory, suppliers_df)

    export_all(
        output_dir,
        spare_parts_catalog=catalog,
        suppliers=suppliers_df,
        inventory_snapshots=inventory,
        part_tickets=tickets,
        purchase_orders=pos,
    )

    n_crisis = len(tickets[tickets["risk"] == "crisis"])
    n_at_risk = len(tickets[tickets["risk"] == "at_risk"])

    if n_crisis < 3:
        logger.warning("Less than 3 crisis scenarios — re-run with different seed")
    if n_at_risk < 3:
        logger.warning("Less than 3 at_risk scenarios — re-run with different seed")

    return {
        "catalog": catalog,
        "suppliers": suppliers_df,
        "inventory": inventory,
        "tickets": tickets,
        "pos": pos,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate mock spare parts data")
    parser.add_argument("--output-dir", default=None, help="Output directory for CSV files")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    if args.seed:
        np.random.seed(args.seed)

    output_dir = Path(args.output_dir) if args.output_dir else None
    generate_all(output_dir)


if __name__ == "__main__":
    main()
