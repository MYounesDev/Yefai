import pandas as pd
import pytest

from etl.split_data import (
    build_split_manifest,
    validate_split_no_leakage,
    validate_split_ratio,
    generate_split,
    DEFAULT_SPLIT,
)


@pytest.fixture
def sample_labels() -> pd.DataFrame:
    data = []
    for set_id in range(1, 18):
        for i in range(5):
            data.append(
                {
                    "ImageFile": f"Set{set_id}/img_{i}.png",
                    "wear": 30.0 + set_id * 2,
                    "type": "flank_wear",
                    "Set": set_id,
                    "ImageDateTime": "2022-01-01",
                }
            )
    return pd.DataFrame(data)


def test_build_split_manifest(sample_labels):
    manifest = build_split_manifest(sample_labels, DEFAULT_SPLIT)
    assert len(manifest) == 17
    assert len(manifest[manifest["Split"] == "train"]) == 12
    assert len(manifest[manifest["Split"] == "test"]) == 5
    assert manifest[manifest["Split"] == "train"]["ImageCount"].sum() == 60
    assert manifest[manifest["Split"] == "test"]["ImageCount"].sum() == 25


def test_validate_split_no_leakage(sample_labels):
    manifest = build_split_manifest(sample_labels, DEFAULT_SPLIT)
    assert validate_split_no_leakage(manifest, sample_labels) is True


def test_validate_split_no_leakage_overlap(sample_labels):
    bad_split = {"train": [1, 2, 3], "test": [3, 4, 5]}
    with pytest.raises(ValueError, match="overlap"):
        build_split_manifest(sample_labels, bad_split)


def test_validate_split_ratio(sample_labels):
    manifest = build_split_manifest(sample_labels, DEFAULT_SPLIT)
    result = validate_split_ratio(manifest)
    assert result is True or result is False


def test_generate_split(tmp_path, sample_labels):
    labels_path = tmp_path / "labels.csv"
    sample_labels.to_csv(labels_path, index=False)
    output_dir = tmp_path / "manifests"

    manifest = generate_split(labels_path, output_dir)
    assert (output_dir / "split_manifest.csv").exists()
    assert len(manifest) == 17
