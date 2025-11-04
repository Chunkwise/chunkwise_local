from fastapi import FastAPI, Body
from chunkwise_core import Chunk, GeneralChunkerConfig
from utils import create_chunker, get_chunks

app = FastAPI()


@app.post("/chunks")
def chunk(
    chunker_config: GeneralChunkerConfig = Body(...), text: str = Body(...)
) -> list[Chunk]:
    chunker = create_chunker(chunker_config)
    return get_chunks(text, chunker)
