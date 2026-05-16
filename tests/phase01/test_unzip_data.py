import tempfile
import zipfile
from pathlib import Path

import pytest

from etl.unzip_data import extract_zips, verify_against_labels


@pytest.fixture
def mock_dataset_dir():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        images_dir = tmp_path / "MATWI" / "Set1" / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        for i in range(3):
            (images_dir / f"img_{i:03d}.png").write_text("fake")

        zip_path = tmp_path / "Set1.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for img in images_dir.iterdir():
                arcname = f"MATWI/Set1/images/{img.name}"
                zf.write(img, arcname)

        yield tmp_path


def test_extract_zips(mock_dataset_dir):
    counts = extract_zips(mock_dataset_dir, mock_dataset_dir / "output")
    assert "Set1" in counts
    assert counts["Set1"] == 3


def test_extract_zips_empty_dir(tmp_path):
    counts = extract_zips(tmp_path, tmp_path / "output")
    assert counts == {}


def test_verify_against_labels(tmp_path):
    labels_csv = tmp_path / "labels.csv"
    labels_csv.write_text(
        "ImageFile,wear,type,Set,ImageDateTime\n"
        "img1.png,30,flank_wear,1,2022-01-01\n"
        "img2.png,60,adhesion,1,2022-01-02\n"
        "img3.png,90,combination,2,2022-01-03\n"
    )

    counts = {"Set1": 2, "Set2": 1}
    assert verify_against_labels(counts, labels_csv) is True


def test_verify_against_labels_missing(tmp_path):
    labels_csv = tmp_path / "labels.csv"
    labels_csv.write_text(
        "ImageFile,wear,type,Set,ImageDateTime\n"
        "img1.png,30,flank_wear,1,2022-01-01\n"
    )
    assert verify_against_labels({}, labels_csv) is False
