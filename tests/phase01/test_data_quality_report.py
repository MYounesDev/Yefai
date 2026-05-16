from pathlib import Path


def test_data_quality_report_exists():
    report_path = (
        Path(__file__).resolve().parent.parent.parent
        / "reports"
        / "data_quality_report.md"
    )
    assert report_path.exists()

    content = report_path.read_text()
    assert "MATWI" in content
    assert "1803" in content
    assert "split" in content.lower()
    assert "Train" in content or "train" in content.lower()


def test_mock_spare_parts_report_exists():
    report_path = (
        Path(__file__).resolve().parent.parent.parent
        / "reports"
        / "mock_spare_parts_report.md"
    )
    assert report_path.exists()

    content = report_path.read_text()
    assert "mock" in content.lower() or "sentetik" in content.lower()
    assert "crisis" in content.lower()
    assert "catalog" in content.lower() or "parça" in content.lower()
