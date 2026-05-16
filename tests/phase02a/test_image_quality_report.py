from pathlib import Path


class TestImageQualityReport:
    def test_report_file_exists(self, project_root):
        report_path = project_root / "reports" / "image_data_quality.md"
        assert report_path.exists(), f"Report not found at {report_path}"

    def test_report_contains_required_sections(self, project_root):
        report_path = project_root / "reports" / "image_data_quality.md"
        text = report_path.read_text()
        assert "Wear Dağılımı" in text
        assert "Anomaly Threshold" in text
        assert "Wear Type Dağılımı" in text
        assert "Split Kontrolü" in text
        assert "Anomalib Formatı" in text
