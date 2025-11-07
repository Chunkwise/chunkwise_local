import os
import requests
from server_types import Chunk, VisualizeRequest

CHUNKING_SERVICE_URL = os.getenv("CHUNKING_SERVICE_URL", "http://localhost:8001")
VISUALIZATION_SERVICE_URL = os.getenv(
    "VISUALIZATION_SERVICE_URL", "http://localhost:8002"
)
EVALUATION_SERVICE_URL = os.getenv("EVALUATION_SERVICE_URL", "http://localhost:8003")


def get_chunks(chunker_config, document) -> list[Chunk]:
    """
    Returns a list of chunks from the chunking service based on
    the passed in configurations and document.
    """
    # Prepare the request for the chunking service
    chunking_payload: VisualizeRequest = {
        "chunker_config": chunker_config.__dict__,
        "text": document,
    }

    # Send request to chunking service
    chunking_response = requests.post(
        f"{CHUNKING_SERVICE_URL}/chunk", json=chunking_payload, timeout=10
    )
    chunking_response.raise_for_status()
    chunks: list[Chunk] = chunking_response.json()
    return chunks


def get_visualization():
    pass


def get_evaluation():
    pass
