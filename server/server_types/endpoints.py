from typing import Literal, Optional
from pydantic import BaseModel
from chunkwise_core import ChunkerConfig, Chunk


class ChunkStatistics(BaseModel):
    total_chunks: int
    largest_chunk_chars: int
    largest_text: str
    smallest_chunk_chars: int
    smallest_text: str
    avg_chars: float


class VisualizeRequest(BaseModel):
    chunker_config: ChunkerConfig
    text: str


class VisualizeResponse(BaseModel):
    stats: ChunkStatistics
    html: str
