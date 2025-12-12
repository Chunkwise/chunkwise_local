from fastapi.testclient import TestClient
from main import app
from chunkwise_core import ChunkerConfig, Chunk
from unittest.mock import MagicMock

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "chunking"}

def test_chunk(mocker):
    mock_chunker = MagicMock()
    # Mock split_text
    mock_chunker.split_text.return_value = ["chunk1", "chunk2"]

    # Patch create_chunker where it is looked up in main
    mock_create_chunker = mocker.patch("main.create_chunker", return_value=mock_chunker)

    config = ChunkerConfig(chunking_strategy="fixed")

    response = client.post(
        "/chunk",
        json={"chunker_config": config.model_dump(), "text": "some text"}
    )
    assert response.status_code == 200
    assert response.json() == ["chunk1", "chunk2"]

def test_chunk_callable(mocker):
    # Mock chunker as callable returning list of objects with text attribute
    mock_chunker = MagicMock()
    del mock_chunker.split_text # Ensure it doesn't have split_text

    chunk1 = MagicMock()
    chunk1.text = "chunk1"
    chunk2 = MagicMock()
    chunk2.text = "chunk2"

    mock_chunker.return_value = [chunk1, chunk2]

    mocker.patch("main.create_chunker", return_value=mock_chunker)

    config = ChunkerConfig(chunking_strategy="fixed")
    response = client.post(
        "/chunk",
        json={"chunker_config": config.model_dump(), "text": "some text"}
    )
    assert response.status_code == 200
    assert response.json() == ["chunk1", "chunk2"]

def test_chunk_with_metadata(mocker):
    mock_chunker = MagicMock()
    mocker.patch("main.create_chunker", return_value=mock_chunker)

    # Mock get_chunks_with_metadata
    mocker.patch("main.get_chunks_with_metadata", return_value=[
        Chunk(text="c1", metadata={"page": 1}),
        Chunk(text="c2", metadata={"page": 2})
    ])

    config = ChunkerConfig(chunking_strategy="fixed")
    response = client.post(
        "/chunk_with_metadata",
        json={"chunker_config": config.model_dump(), "text": "text"}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2
    assert result[0]["text"] == "c1"
    assert result[0]["metadata"] == {"page": 1}
