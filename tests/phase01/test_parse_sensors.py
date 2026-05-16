from pathlib import Path

import pandas as pd

from etl.parse_sensors import (
    parse_sensor_csv,
    parse_set_sensors,
    parse_all_sensors,
    get_sensor_summary,
)


def test_parse_sensor_csv_valid(tmp_path):
    csv_path = tmp_path / "sensor.csv"
    csv_path.write_text("t,ch1,ch2,ch3,ch4,ch5\n0,1,2,3,4,5\n1,6,7,8,9,10\n")

    df = parse_sensor_csv(csv_path)
    assert df is not None
    assert df.shape == (2, 6)


def test_parse_sensor_csv_wrong_columns(tmp_path):
    csv_path = tmp_path / "sensor.csv"
    csv_path.write_text("t,ch1\n0,1\n")
    df = parse_sensor_csv(csv_path)
    assert df is not None


def test_parse_sensor_csv_read_error(tmp_path):
    csv_path = tmp_path / "nonexistent.csv"
    df = parse_sensor_csv(csv_path)
    assert df is None


def test_parse_set_sensors(tmp_path):
    set_dir = tmp_path / "Set1"
    sensor_dir = set_dir / "sensordata"
    sensor_dir.mkdir(parents=True)

    (sensor_dir / "Accelerometer_001.csv").write_text(
        "t,ch1,ch2,ch3,ch4,ch5\n0,1,2,3,4,5\n"
    )
    (sensor_dir / "Acoustic_001.csv").write_text(
        "t,ch1,ch2,ch3,ch4,ch5\n0,10,20,30,40,50\n"
    )

    sensors = parse_set_sensors(set_dir)
    assert len(sensors) >= 2


def test_parse_set_sensors_missing_dir(tmp_path):
    set_dir = tmp_path / "Set1"
    set_dir.mkdir()
    sensors = parse_set_sensors(set_dir)
    assert sensors == {}


def test_get_sensor_summary():
    df_acc = pd.DataFrame({"t": [0, 1], "ch1": [1, 2], "ch2": [3, 4], "ch3": [5, 6], "ch4": [7, 8], "ch5": [9, 10]})
    all_sensors = {1: {"Accelerometer/acc": df_acc}}
    summary = get_sensor_summary(all_sensors)
    assert len(summary) == 1
    assert summary.iloc[0]["Rows"] == 2
    assert summary.iloc[0]["Columns"] == 6
