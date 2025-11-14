"""Chunking Service"""

from fastapi import FastAPI, Body
from chunkwise_core import Chunk, ChunkerConfig, create_chunker
from get_chunks_with_metadata import get_chunks_with_metadata

app = FastAPI()


@app.post("/chunk")
def chunk(
    chunker_config: ChunkerConfig = Body(...), text: str = Body(...)
) -> list[str]:
    """
    Receives a chunking configuration and a string to be chunked
    Returns an array of strings
    """
    chunker = create_chunker(chunker_config)

    if hasattr(chunker, "split_text"):
        return chunker.split_text(text)
    return [chunk.text for chunk in chunker(text)]


@app.post("/chunk_with_metadata")
def chunk_with_metadata(
    chunker_config: ChunkerConfig = Body(...), text: str = Body(...)
) -> list[Chunk]:
    """
    Receives a chunking configuration and a string to be chunked
    Returns an array of chunks with metadata
    """
    chunker = create_chunker(chunker_config)
    return get_chunks_with_metadata(chunker, text)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "chunking"}
