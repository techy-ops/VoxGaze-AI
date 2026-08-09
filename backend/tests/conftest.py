import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path for test runner resolution
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app


@pytest.fixture(scope="module")
def client():
    """
    TestClient fixture for executing endpoint assertions.
    """
    with TestClient(app) as test_client:
        yield test_client
