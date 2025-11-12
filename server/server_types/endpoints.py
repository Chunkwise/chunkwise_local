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
