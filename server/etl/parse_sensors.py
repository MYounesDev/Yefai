import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_SENSOR_TYPES = ["Accelerometer", "Acoustic", "Force_X", "Force_Y", "Force_Z"]
EXPECTED_COLUMN_COUNT = 6


def parse_sensor_csv(csv_path: Path) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logger.error("Failed to read %s: %s", csv_path, e)
        return None

    if df.shape[1] != EXPECTED_COLUMN_COUNT:
        logger.warning(
            "%s: expected %d columns, got %d (file: %s)",
            csv_path.name,
            EXPECTED_COLUMN_COUNT,
            df.shape[1],
            csv_path,
        )

    first_col = df.columns[0]
    try:
        df[first_col] = pd.to_datetime(df[first_col], errors="coerce")
    except Exception:
        pass

    return df


def parse_set_sensors(set_dir: Path) -> Dict[str, pd.DataFrame]:
    sensor_dir = set_dir / "sensordata"
    if not sensor_dir.exists():
        logger.warning("Sensor directory not found: %s", sensor_dir)
        return {}

    results: Dict[str, pd.DataFrame] = {}
    for sensor_type in EXPECTED_SENSOR_TYPES:
        pattern = f"*{sensor_type}*.csv"
        matches = list(sensor_dir.glob(pattern))

        if not matches:
            logger.warning("No %s CSV found in %s", sensor_type, sensor_dir)
            continue

        for csv_file in matches:
            key = f"{sensor_type}/{csv_file.stem}"
            df = parse_sensor_csv(csv_file)
            if df is not None:
                results[key] = df
                logger.info(
                    "Parsed %s: %d rows × %d cols", key, len(df), df.shape[1]
                )

    return results


def parse_all_sensors(matwi_root: Path) -> Dict[int, Dict[str, pd.DataFrame]]:
    all_sensors: Dict[int, Dict[str, pd.DataFrame]] = {}
    set_dirs = sorted(matwi_root.glob("Set*"))

    if not set_dirs:
        logger.warning("No Set directories found in %s", matwi_root)
        return all_sensors

    for set_dir in set_dirs:
        set_num = int(set_dir.name.replace("Set", ""))
        sensors = parse_set_sensors(set_dir)
        if sensors:
            all_sensors[set_num] = sensors
        else:
            logger.warning("No sensor data found for Set %d", set_num)

    logger.info(
        "Parsed sensors for %d/%d sets",
        len(all_sensors),
        len(set_dirs),
    )
    return all_sensors


def get_sensor_summary(all_sensors: Dict[int, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
    rows = []
    for set_num, sensors in all_sensors.items():
        for key, df in sensors.items():
            rows.append(
                {
                    "Set": set_num,
                    "SensorFile": key,
                    "Rows": len(df),
                    "Columns": df.shape[1],
                    "HasTimestamp": "timestamp" in key.lower()
                    or pd.api.types.is_datetime64_any_dtype(df.iloc[:, 0]),
                }
            )
    return pd.DataFrame(rows)
