from pathlib import Path


def test_mock_spare_parts_report_has_crisis():
    report_path = (
        Path(__file__).resolve().parent.parent.parent
        / "reports"
        / "mock_spare_parts_report.md"
    )
    content = report_path.read_text()
    assert "Crisis (score > 70)" in content or "crisis" in content.lower()
    assert "ready_for_review" in content.lower()


def test_mock_csv_files_exist():
    data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "mock"
    files = [
        "spare_parts_catalog.csv",
        "suppliers.csv",
        "inventory_snapshots.csv",
        "part_tickets.csv",
        "purchase_orders.csv",
    ]
    import pandas as pd

    for f in files:
        path = data_dir / f
        assert path.exists(), f"Missing: {f}"
        df = pd.read_csv(path)
        assert len(df) > 0, f"Empty: {f}"
