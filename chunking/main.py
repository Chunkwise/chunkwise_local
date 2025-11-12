"""Chunking Service"""

from fastapi import FastAPI, Body
from chunkwise_core import Chunk, ChunkerConfig, create_chunker

app = FastAPI()


@app.post("/chunk")
def chunk(
    chunker_config: ChunkerConfig = Body(...), text: str = Body(...)
) -> list[Chunk] | list[str]:
    """
    Receives a chunking configuration and a string to be chunked
    Returns an array of chunks (Chonkie chunks have metadata, Langchain chunks are strings)
    """
    chunker = create_chunker(chunker_config)

    # LangChain chunkers are called with `split_text`
    if hasattr(chunker, "split_text"):
        return chunker.split_text(text)
    # Chonkie chunkers are callable objects (with __call__)
    return chunker(text)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "chunking"}
