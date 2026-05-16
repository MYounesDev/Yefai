import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))


@pytest.fixture
def sample_labels_df():
    return pd.DataFrame(
        {
            "ImageFile": [
                "MATWI/Set1/image_001.jpg",
                "MATWI/Set1/image_002.jpg",
                "MATWI/Set15/image_050.jpg",
                "MATWI/Set15/image_051.jpg",
            ],
            "wear": [30.0, 40.0, 95.0, 100.0],
            "type": [
                "flank_wear",
                "flank_wear",
                "flank_wear+adhesion",
                "adhesion",
            ],
            "Set": [1, 1, 15, 15],
        }
    )


@pytest.fixture
def sample_splits():
    return {
        "train": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "test": [13, 14, 15, 16, 17],
    }


@pytest.fixture
def tmp_anomalib_dir(tmp_path: Path):
    d = tmp_path / "anomalib_format"
    d.mkdir()
    return d
