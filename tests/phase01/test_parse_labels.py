import pandas as pd
import pytest

from etl.parse_labels import (
    normalize_wear_type,
    parse_labels,
    parse_sets,
    parse_metadata,
)


def test_normalize_wear_type():
    assert normalize_wear_type("flank_wear") == "flank_wear"
    assert normalize_wear_type("adhesion") == "adhesion"
    assert normalize_wear_type("flank_wear+adhesion") == "combination"
    assert normalize_wear_type("") == "unknown"
    assert normalize_wear_type(None) == "unknown"


def test_parse_labels(tmp_path):
    csv_path = tmp_path / "labels.csv"
    csv_path.write_text(
        "ImageFile,wear,type,Set,ImageDateTime,SensorFile,SensorDateTime\n"
        "img1.png,30,flank_wear,1,2022-01-01 12:00:00,sens1.csv,2022-01-01 11:59:00\n"
        "img2.png,60,adhesion,2,2022-01-02 12:00:00,sens2.csv,2022-01-02 11:59:00\n"
        "img3.png,90,flank_wear+adhesion,3,2022-01-03 12:00:00,sens3.csv,2022-01-03 11:59:00\n"
    )

    df = parse_labels(csv_path)
    assert len(df) == 3
    assert df["wear"].dtype == float
    assert pd.api.types.is_datetime64_any_dtype(df["ImageDateTime"])
    assert df["wear_type"].tolist() == ["flank_wear", "adhesion", "combination"]


def test_parse_labels_missing_columns(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("ImageFile,wear\nimg1.png,30\n")
    with pytest.raises(ValueError, match="missing columns"):
        parse_labels(csv_path)


def test_parse_sets(tmp_path):
    csv_path = tmp_path / "sets.csv"
    csv_path.write_text(
        ",Vc,n,fz,Vf,Ae,Ap,material,crop,Coating,z\n"
        'Set 1,?,?,?,?,1,1,CK45,"2470, 1000, 3070, 1400",,1\n'
        'Set 2,120,2547,0.08,203,1,1,CK45,"1150, 670, 1750, 1070",,1\n'
    )

    df = parse_sets(csv_path)
    assert len(df) == 2
    assert df["Set"].tolist() == [1, 2]


def test_parse_metadata(tmp_path):
    labels_csv = tmp_path / "labels.csv"
    labels_csv.write_text(
        "ImageFile,wear,type,Set,ImageDateTime\nimg1.png,30,flank_wear,1,2022-01-01\n"
    )
    sets_csv = tmp_path / "sets.csv"
    sets_csv.write_text(
        ",Vc,n,fz,Vf,Ae,Ap,material,crop,Coating,z\n"
        'Set 1,?,?,?,?,1,1,CK45,"0,0,0,0",,1\n'
    )

    labels, sets = parse_metadata(labels_csv, sets_csv)
    assert len(labels) == 1
    assert len(sets) == 1
