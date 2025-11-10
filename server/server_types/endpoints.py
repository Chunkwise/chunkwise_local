from typing import Optional
from pydantic import BaseModel, Optional
from chunkwise_core import ChunkerConfig, Chunk, EvaluationResponse


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


class Evaluations(BaseModel):
    """
    Metrics sent to the frontend about a chunking configurations evaluation.
    """

    omega_precision: float
    precision: float
    recall: float
    iou: float


class VisualizeRequest(BaseModel):
    """
    Request received to visualize a document.
    """

    chunker_config: ChunkerConfig
    text: str


class VisualizeResponse(BaseModel):
    """
    Response to a VisualizeRequest.
    """

    stats: ChunkStatistics
    html: str


class Workflow(BaseModel):
    id: Optional[int]
    document_id: Optional[int]
    chunking_strategy: Optional[ChunkerConfig]
    chunks_stats: Optional[ChunkStatistics]
    visualization_html: Optional[str]
    eval_metrics: Optional[EvaluationResponse]
