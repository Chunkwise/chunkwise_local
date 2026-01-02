from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_configs():
    response = client.get("/api/configs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_document(mocker):
    # Mock create_file, upload_s3_file, delete_file
    mocker.patch("main.create_file")
    mocker.patch("main.upload_s3_file", return_value=None)
    mocker.patch("main.delete_file")

    response = client.post(
        "/api/documents",
        json={"document_title": "test_doc", "document_content": "This is a test document."}
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Successfully uploaded test_doc"}

def test_upload_document_invalid_title():
    response = client.post(
        "/api/documents",
        json={"document_title": "invalid/title", "document_content": "content"}
    )
    assert response.status_code == 400

def test_upload_document_empty_content():
    response = client.post(
        "/api/documents",
        json={"document_title": "test_doc", "document_content": ""}
    )
    assert response.status_code == 400

def test_delete_document(mocker):
    mocker.patch("main.delete_s3_file", return_value=None)
    response = client.delete("/api/documents/test_doc")
    assert response.status_code == 200
    assert response.json() == {"detail": "deleted"}

def test_get_documents(mocker):
    mocker.patch("main.get_s3_file_names", return_value=["doc1.txt", "doc2.txt"])
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == ["doc1.txt", "doc2.txt"]

def test_create_workflow(mocker):
    mocker.patch("main.create_workflow", return_value={"id": 1, "title": "New Workflow"})
    response = client.post("/api/workflows", json={"title": "New Workflow"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "New Workflow"}

def test_get_workflows(mocker):
    mocker.patch("main.get_all_workflows", return_value=[{"id": 1, "title": "W1"}])
    response = client.get("/api/workflows")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "title": "W1"}]

def test_remove_workflow(mocker):
    mocker.patch("main.delete_workflow", return_value=True)
    response = client.delete("/api/workflows/1")
    assert response.status_code == 200

def test_visualize(mocker):
    # Mock dependent services
    mocker.patch("main.get_workflow_info", return_value=("doc.txt", MagicMock()))
    mocker.patch("main.download_s3_file")

    # Mock file reading
    mocker.patch("builtins.open", mocker.mock_open(read_data="Document content"))

    mocker.patch("main.get_chunks", return_value=[
        MagicMock(text="Chunk 1"), MagicMock(text="Chunk 2")
    ])

    mocker.patch("main.calculate_chunk_stats", return_value={
        "total_chunks": 2,
        "avg_chars": 7,
        "largest_chunk_chars": 7,
        "largest_text": "Chunk 1",
        "smallest_chunk_chars": 7,
        "smallest_text": "Chunk 1"
    })

    mock_viz = MagicMock()
    mock_viz.get_html.return_value = "<html></html>"
    mocker.patch("main.Visualizer", return_value=mock_viz)

    mocker.patch("main.delete_file")
    mocker.patch("main.update_workflow")

    response = client.get("/api/workflows/1/visualization")
    assert response.status_code == 200
    assert "stats" in response.json()
    assert "html" in response.json()
