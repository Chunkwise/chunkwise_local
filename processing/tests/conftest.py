import sys
from unittest.mock import MagicMock
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

# Reuse the same mock structure
class MockChunkerConfig(BaseModel):
    chunking_strategy: str = "fixed"
    chunk_size: int = 100
    chunk_overlap: int = 0
    model_config = {"extra": "allow"}

class MockChunk(BaseModel):
    text: Optional[str] = None
    metadata: dict = {}
    model_config = {"extra": "allow"}

# Create a mock module
mock_chunkwise_core = MagicMock()
mock_chunkwise_core.ChunkerConfig = MockChunkerConfig
mock_chunkwise_core.Chunk = MockChunk

# Mock utils inside chunkwise_core
mock_utils = MagicMock()
mock_utils.create_chunker = MagicMock(return_value=MagicMock())
mock_chunkwise_core.utils = mock_utils

# Install the mock module
sys.modules["chunkwise_core"] = mock_chunkwise_core
sys.modules["chunkwise_core.utils"] = mock_utils

import pytest
import os

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set environment variables for testing."""
    monkeypatch.setenv("VECTOR_DB_HOST", "localhost")
    monkeypatch.setenv("VECTOR_DB_PORT", "5432")
    monkeypatch.setenv("VECTOR_DB_NAME", "test_db")
    monkeypatch.setenv("VECTOR_DB_USER", "user")
    monkeypatch.setenv("VECTOR_DB_PASSWORD", "password")
    monkeypatch.setenv("VECTOR_DB_TABLE", "test_table")
    monkeypatch.setenv("BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
