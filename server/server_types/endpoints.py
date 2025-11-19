"""
Provides some custom types to the server.
"""

from pydantic import BaseModel
from chunkwise_core import ChunkerConfig, Chunk, EvaluationResponse, EvaluationMetrics


class ChunkStatistics(BaseModel):
    """
    Statistics about a list of chunks.
    """

    total_chunks: int
    largest_chunk_chars: int
    largest_text: str
    smallest_chunk_chars: int
    smallest_text: str
    avg_chars: float


class VisualizeResponse(BaseModel):
    """
    Response to a VisualizeRequest.
    """

    stats: ChunkStatistics
    html: str


class Workflow(BaseModel):
    """
    Shape of an object in the workflow table of the database.
    """

    id: int | None = None
    document_title: str | None = None
    chunking_strategy: ChunkerConfig | str | None = None
    chunks_stats: ChunkStatistics | str | None = None
    visualization_html: str | None = None
    evaluation_metrics: EvaluationMetrics | str | None = None


class DeployRequest(BaseModel):
    workflow_id: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str | None = None