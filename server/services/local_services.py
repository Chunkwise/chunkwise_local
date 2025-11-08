"""
Contains service calls to the services implemented by the chunkwise team.
"""

import os
import requests
from server_types import Chunk, VisualizeRequest, EvaluationResponse

CHUNKING_SERVICE_URL = os.getenv("CHUNKING_SERVICE_URL", "http://localhost:8001")
VISUALIZATION_SERVICE_URL = os.getenv(
    "VISUALIZATION_SERVICE_URL", "http://localhost:8002"
)
EVALUATION_SERVICE_URL = os.getenv("EVALUATION_SERVICE_URL", "http://localhost:8003")


async def get_chunks(chunker_config, document) -> list[Chunk]:
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


async def get_visualization(chunks: list[Chunk]) -> str:
    """
    Takes a list of chunks and returns the HTML to visualize those
    chunks, gotten from the visualization server.
    """
    # Send chunks to visualization service
    visualization_response = requests.post(
        f"{VISUALIZATION_SERVICE_URL}/visualize", json=chunks, timeout=10
    )
    visualization_response.raise_for_status()

    # Get the text from the response
    visualization_html = visualization_response.text
    return visualization_html


async def get_evaluation(chunker_config, document_id) -> EvaluationResponse:
    """
    Takes a chunking configuration and a documet id, returns an
    EvaluationResponse from the evaluation service.
    """
    request_body = {
        "chunker_config": chunker_config.__dict__,
        "document_id": document_id,
    }

    # Send request to chunking service
    evaluation_response = requests.post(
        f"{EVALUATION_SERVICE_URL}/evaluate", json=request_body, timeout=120
    )
    evaluation_response.raise_for_status()
    evaluation_json: EvaluationResponse = evaluation_response.json()
    return evaluation_json
