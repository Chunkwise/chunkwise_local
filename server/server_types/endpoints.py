"""
Provides some custom types to the server.
"""

from typing import Optional
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

    id: Optional[int] = None
    document_title: Optional[str] = None
    chunking_strategy: Optional[ChunkerConfig] = None
    chunks_stats: Optional[ChunkStatistics] = None
    visualization_html: Optional[str] = None
    evaluation_metrics: Optional[EvaluationMetrics] = None
