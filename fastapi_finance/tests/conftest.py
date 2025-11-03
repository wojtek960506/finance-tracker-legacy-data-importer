import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
  """
  Provides a reusable TestClient instance for the FastAPI app.
  Scoped per module to improve speed while isolating tests.
  """
  with TestClient(app) as test_client:
    yield test_client
