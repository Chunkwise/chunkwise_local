"""
Contains service calls to the services implemented by the chunkwise team.
"""

import os
import requests
from server_types import EvaluationResponse

EVALUATION_SERVICE_URL = os.getenv("EVALUATION_SERVICE_URL", "http://localhost:8003")


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
        f"{EVALUATION_SERVICE_URL}/evaluate", json=request_body, timeout=120
    )
    evaluation_response.raise_for_status()
    evaluation_json: EvaluationResponse = evaluation_response.json()
    return evaluation_json
