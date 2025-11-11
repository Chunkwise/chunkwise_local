"""Chunking Service"""

from fastapi import FastAPI, Body
from chunkwise_core import Chunk, ChunkerConfig, create_chunker
from utils import get_chunks

app = FastAPI()


@app.post("/chunk")
def chunk(
    chunker_config: ChunkerConfig = Body(...), text: str = Body(...)
) -> list[Chunk]:
    """
    Receives a chunking configuration and a string to be chunked
    Returns an array of chunks (strings with metadata)
    """
    chunker = create_chunker(chunker_config)
    return get_chunks(text, chunker)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "chunking"}
