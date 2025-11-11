from typing import Optional
from pydantic import BaseModel
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

    omega_precision: float | int
    precision: float | int
    recall: float | int
    iou: float | int


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
    id: Optional[int] = None
    document_title: Optional[str] = None
    chunking_strategy: Optional[ChunkerConfig] = None
    chunks_stats: Optional[ChunkStatistics] = None
    visualization_html: Optional[str] = None
    evaluation_metrics: Optional[Evaluations] = None


class DocumentUpload(BaseModel):
    document_title: str
    document_content: str
