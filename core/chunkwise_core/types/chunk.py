from pydantic import BaseModel


class Chunk(BaseModel):
    text: str  # The chunk text
    start_index: int  # Starting position in original text
    end_index: int  # Ending position in original text
    token_count: int | None = None  # Number of tokens in Chunk
