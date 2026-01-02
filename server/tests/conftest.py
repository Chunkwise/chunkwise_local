import sys
from unittest.mock import MagicMock
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

# Define mock classes for chunkwise_core
class MockChunkerConfig(BaseModel):
    chunking_strategy: str = "fixed"
    chunk_size: int = 100
    chunk_overlap: int = 0
    model_config = {"extra": "allow"}

class MockChunk(BaseModel):
    text: Optional[str] = None
    metadata: dict = {}
    model_config = {"extra": "allow"}

class MockEvaluationMetrics(BaseModel):
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    model_config = {"extra": "allow"}

class MockEvaluationResponse(BaseModel):
    metrics: List[MockEvaluationMetrics] = []
    model_config = {"extra": "allow"}

class MockEvaluationRequest(BaseModel):
    document_id: str
    chunker_config: MockChunkerConfig
    model_config = {"extra": "allow"}

class MockQueryGenerationConfig(BaseModel):
    model_config = {"extra": "allow"}

# Create a mock module
mock_chunkwise_core = MagicMock()
mock_chunkwise_core.ChunkerConfig = MockChunkerConfig
mock_chunkwise_core.Chunk = MockChunk
mock_chunkwise_core.EvaluationMetrics = MockEvaluationMetrics
mock_chunkwise_core.EvaluationResponse = MockEvaluationResponse
mock_chunkwise_core.EvaluationRequest = MockEvaluationRequest
mock_chunkwise_core.QueryGenerationConfig = MockQueryGenerationConfig

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
    monkeypatch.setenv("VECTOR_DB_SECRET_NAME", "test_secret")
    monkeypatch.setenv("EMBEDDING_DIM", "1536")

@pytest.fixture
def mock_boto3(mocker):
    """Mock boto3 client."""
    mock_boto = mocker.patch("boto3.client")
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3
    return mock_boto

@pytest.fixture
def mock_psycopg2(mocker):
    """Mock psycopg2."""
    return mocker.patch("psycopg2.connect")
