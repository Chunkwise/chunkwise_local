from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from chunkwise_core import ChunkerConfig, EvaluationRequest
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "evaluation"}

def test_evaluate_chunking(mocker):
    # Mock evaluate service
    mock_evaluate_response = MagicMock()
    mock_evaluate_response.model_dump.return_value = {"metrics": []}

    # Patch the evaluate service where it is imported in main
    mocker.patch("main.evaluate", return_value=mock_evaluate_response)

    request_data = {
        "document_id": "doc1",
        "chunker_config": {"chunking_strategy": "fixed"}
    }

    response = client.post("/evaluate", json=request_data)
    assert response.status_code == 200

def test_evaluate_chunking_error(mocker):
    mocker.patch("main.evaluate", side_effect=Exception("Something went wrong"))

    request_data = {
        "document_id": "doc1",
        "chunker_config": {"chunking_strategy": "fixed"}
    }

    response = client.post("/evaluate", json=request_data)
    assert response.status_code == 500
    assert "Unexpected error" in response.json()["detail"]
