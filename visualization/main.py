from fastapi import FastAPI
from pydantic import BaseModel
from utils.viz import Visualizer

app = FastAPI()

class ChonkieChunk(BaseModel):
    text: str           # The chunk text
    start_index: int    # Starting position in original text
    end_index: int      # Ending position in original text
    token_count: int    # Number of tokens in Chunk


class Item(BaseModel):
    chunks: list[ChonkieChunk]   # List of Chonkie-formatted chunks


@app.post("/visualization")
def visualize(item: Item):
    viz = Visualizer()
    viz.save("test.html", item.chunks) # Save to file
