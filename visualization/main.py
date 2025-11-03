from fastapi import FastAPI
from pydantic import BaseModel
from utils.viz import Visualizer

# from chonkie.types import Chunk
from typing import List, Optional

app = FastAPI()


class Chunk(BaseModel):
    text: str  # The chunk text
    start_index: int  # Starting position in original text
    end_index: int  # Ending position in original text
    token_count: Optional[int] = None  # Number of tokens in Chunk


@app.post("/visualization")
def visualize(chunks: List[Chunk]) -> str:
    """
    Receives chunks from server
    Sends visualization (HTML) to server
    """
    viz = Visualizer()
    return viz.get_HTML(chunks)
