from fastapi import FastAPI
from typing import List
from utils import Visualizer, save_to_file
from chunkwise_core import Chunk

app = FastAPI()


@app.post("/visualization")
def visualize(chunks: List[Chunk]) -> str:
    """
    Receives chunks from server
    Sends visualization (HTML) to server
    """
    viz = Visualizer()
    html_content = viz.get_HTML(chunks)
    # For testing purposes only. Saves to ./example_visualizations/visualization.html
    # save_to_file(html_content)
    return html_content
