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
    html_content = viz.get_HTML(chunks)
    save_to_file(html_content)
    return html_content


def save_to_file(html_content):
    try:
        import os

        filepath = os.path.abspath("visualization.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML visualization saved to: file://{filepath}")
    except IOError as e:
        raise IOError(f"Error: Could not write file '{filename}': {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during file saving: {e}")
