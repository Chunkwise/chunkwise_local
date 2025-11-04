from typing import List, Union
from pydantic import BaseModel
from .chunker_config import RecursiveChunkerConfig, TokenChunkerConfig


class ChunkingResult(BaseModel):
    iou_mean: float
    recall_mean: float
    precision_mean: float
    precision_omega_mean: float
    chunker_config: Union[RecursiveChunkerConfig, TokenChunkerConfig]


class EvaluateResponse(BaseModel):
    embedding_model: str
    document_id: str
    chunkers_evaluated: List[str]
    results: List[ChunkingResult]
