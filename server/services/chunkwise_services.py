"""
Contains service calls to the services implemented by the chunkwise team.
"""

import requests
from server_types import EvaluationResponse, Chunk
from config import (
    CHUNKING_SERVICE_HOST,
    CHUNKING_SERVICE_PORT,
    EVALUATION_SERVICE_HOST,
    EVALUATION_SERVICE_PORT,
)


async def get_chunks(chunker_config, document) -> list[Chunk]:
    """
    Returns a list of chunks from the chunking service based on
    the passed in configurations and document.
    """
    # Prepare the request for the chunking
    request_body = {
        "chunker_config": chunker_config.model_dump(),
        "text": document,
    }

    # Send request to chunking service
    print(
        f"Sending request to http://{CHUNKING_SERVICE_HOST}:{CHUNKING_SERVICE_PORT}/chunk_with_metadata"
    )
    chunking_response = requests.post(
        f"http://{CHUNKING_SERVICE_HOST}:{CHUNKING_SERVICE_PORT}/chunk_with_metadata",
        json=request_body,
        timeout=120,
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
        "chunking_configs": [chunker_config.model_dump()],
        "document_id": document_id,
    }

    # Send request to chunking service
    print(
        f"Sending request to http://{EVALUATION_SERVICE_HOST}:{EVALUATION_SERVICE_PORT}/evaluate"
    )
    evaluation_response = requests.post(
        f"http://{EVALUATION_SERVICE_HOST}:{EVALUATION_SERVICE_PORT}/evaluate",
        json=request_body,
        timeout=240,
    )
    evaluation_response.raise_for_status()
    evaluation_json: EvaluationResponse = evaluation_response.json()
    return evaluation_json
