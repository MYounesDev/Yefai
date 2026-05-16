import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "server"))


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def server_root() -> Path:
    return PROJECT_ROOT / "server"


@pytest.fixture
def dataset_dir(server_root: Path) -> Path:
    return server_root / "dataset"


@pytest.fixture
def data_dir(project_root: Path) -> Path:
    return project_root / "data"


@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    client.table = MagicMock()
    client.rpc = MagicMock()
    return client


@pytest.fixture
def sample_labels_csv(server_root: Path) -> Path:
    return server_root / "dataset" / "labels.csv"


@pytest.fixture
def sample_sets_csv(server_root: Path) -> Path:
    return server_root / "dataset" / "sets.csv"
