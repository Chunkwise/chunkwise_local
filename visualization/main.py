from fastapi import FastAPI
from typing import List
from viz import Visualizer
from models import Chunk

# I am using the same Chunk type as used in server and evaluation as opposed to Chonkie's Chunk type which has more properties
# If we switch to Chonkie's make sure to change this file and viz.py
# from chonkie.types import Chunk

app = FastAPI()


@app.post("/visualization")
def visualize(chunks: List[Chunk]) -> str:
    """
    Receives chunks from server
    Sends visualization (HTML) to server
    """
    viz = Visualizer()
    return viz.get_HTML(chunks)
