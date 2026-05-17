from pathlib import Path


from ai.anomalib.dataset import build_anomalib_folder_structure, classify_anomaly


class TestClassifyAnomaly:
    def test_normal_wear(self):
        assert classify_anomaly(30.0) == 0
        assert classify_anomaly(45.0) == 0

    def test_anomaly_wear(self):
        assert classify_anomaly(90.0) == 1
        assert classify_anomaly(120.0) == 1

    def test_mild_wear_excluded(self):
        assert classify_anomaly(50.0) is None
        assert classify_anomaly(75.0) is None
        assert classify_anomaly(89.0) is None


class TestBuildAnomalibFolder:
    def test_creates_folder_structure(
        self, sample_labels_df, sample_splits, tmp_anomalib_dir, tmp_path, monkeypatch
    ):

        src_dir = tmp_path / "images"
        src_dir.mkdir()
        for img_file in sample_labels_df["ImageFile"]:
            img_path = src_dir / Path(img_file).name
            img_path.write_bytes(b"fake_image_data")
            monkeypatch.setattr(
                "ai.anomalib.dataset.find_image_path",
                lambda row, root: img_path,
            )

        counts = build_anomalib_folder_structure(
            sample_labels_df,
            tmp_anomalib_dir,
            tmp_path,
            splits=sample_splits,
        )

        assert counts["train/good"] == 2
        assert counts["test/good"] == 0
        assert counts["test/bad"] == 2
        assert (tmp_anomalib_dir / "train" / "good").exists()
        assert (tmp_anomalib_dir / "test" / "good").exists()
        assert (tmp_anomalib_dir / "test" / "bad").exists()

    def test_no_split_overlap(self, sample_splits):
        train = set(sample_splits["train"])
        test = set(sample_splits["test"])
        assert train.isdisjoint(test)
