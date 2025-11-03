from pydantic import BaseModel
from typing import Optional


class Chunk(BaseModel):
    text: str  # The chunk text
    start_index: int  # Starting position in original text
    end_index: int  # Ending position in original text
    token_count: Optional[int] = None  # Number of tokens in Chunk
