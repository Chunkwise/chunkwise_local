"""
Contains service calls to the services implemented by the chunkwise team.
"""

import os
import json
import requests
from server_types import EvaluationResponse, Chunk


CHUNKING_SERVICE_URL = os.getenv("CHUNKING_SERVICE_URL", "http://localhost:8001")
EVALUATION_SERVICE_URL = os.getenv("EVALUATION_SERVICE_URL", "http://localhost:8003")


async def get_chunks(chunker_config, document) -> list[Chunk]:
    """
    Returns a list of chunks from the chunking service based on
    the passed in configurations and document.
    """
    # Prepare the request for the chunking
    request_body = {
        "chunker_config": json.loads(chunker_config.model_dump_json()),
        "text": document,
    }

    # Send request to chunking service
    chunking_response = requests.post(
        f"{CHUNKING_SERVICE_URL}/chunk_with_metadata", json=request_body, timeout=10
    )
    chunking_response.raise_for_status()
    chunks: list[Chunk] = [Chunk(**c) for c in chunking_response.json()]
    return chunks


async def get_evaluation(chunker_config, document_id) -> EvaluationResponse:
    """
    Takes a chunking configuration and a documet id, returns an
    EvaluationResponse from the evaluation service.
    """
    request_body = {
        "chunking_configs": [chunker_config.__dict__],
        "document_id": document_id,
    }

    # Send request to chunking service
    evaluation_response = requests.post(
        f"{EVALUATION_SERVICE_URL}/evaluate", json=request_body, timeout=240
    )
    evaluation_response.raise_for_status()
    evaluation_json: EvaluationResponse = evaluation_response.json()
    return evaluation_json
