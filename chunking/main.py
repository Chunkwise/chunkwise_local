from fastapi import FastAPI, Body
from chunkwise_core import Chunk, ChunkerConfig, create_chunker
from utils import get_chunks

app = FastAPI()


@app.post("/chunk")
def chunk(
    chunker_config: ChunkerConfig = Body(...), text: str = Body(...)
) -> list[Chunk]:
    chunker = create_chunker(chunker_config)
    return get_chunks(text, chunker)
