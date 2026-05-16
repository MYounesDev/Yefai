import tempfile
from pathlib import Path

import pandas as pd
import pytest

from etl.seed_database import (
    prepare_set_records,
    prepare_image_records,
    seed_local_csv,
)


@pytest.fixture
def sample_labels() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ImageFile": [
                "MATWI/Set1/images/img_001.png",
                "MATWI/Set1/images/img_002.png",
                "MATWI/Set2/images/img_001.png",
            ],
            "wear": [30.0, 60.0, 90.0],
            "type": ["flank_wear", "adhesion", "flank_wear+adhesion"],
            "Set": [1, 1, 2],
            "ImageDateTime": ["2022-01-01", "2022-01-02", "2022-01-03"],
            "wear_type": ["flank_wear", "adhesion", "combination"],
        }
    )


def test_prepare_set_records(sample_labels):
    records = prepare_set_records(sample_labels)
    assert len(records) == 2
    assert records[0]["name"] == "Set1"
    assert records[0]["image_count"] == 2
    assert records[1]["name"] == "Set2"
    assert records[1]["image_count"] == 1


def test_prepare_image_records(sample_labels):
    records = prepare_image_records(sample_labels)
    assert len(records) == 3
    assert records[0]["wear_type"] == "flank_wear"
    assert records[0]["flank_wear"] == 30.0
    assert records[2]["wear_type"] == "combination"
    assert records[2]["combination_wear"] == 90.0
    assert "file_path" in records[0]
    assert "MATWI" in records[0]["file_path"]


def test_seed_local_csv(sample_labels):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        set_records = prepare_set_records(sample_labels)
        image_records = prepare_image_records(sample_labels)
        seed_local_csv(set_records, image_records, out)

        assert (out / "sets.csv").exists()
        assert (out / "images.csv").exists()

        sets_df = pd.read_csv(out / "sets.csv")
        assert len(sets_df) == 2

        images_df = pd.read_csv(out / "images.csv")
        assert len(images_df) == 3
