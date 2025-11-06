"""
This is the backend server which acts as a gateway for the client to access
services and it will eventually manage the database(s) and document storage.
"""

import os
from server_types import (
    Chunk,
    ChunkerConfig,
    ChunkStatistics,
    VisualizeResponse,
    VisualizeRequest,
    DocumentPostResponse,
)
from utils import calculate_chunk_stats, normalize_document
from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()
router = APIRouter()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CHUNKING_SERVICE_URL = os.getenv("CHUNKING_SERVICE_URL", "http://localhost:8001")
VISUALIZATION_SERVICE_URL = os.getenv(
    "VISUALIZATION_SERVICE_URL", "http://localhost:8002"
)
EVALUATION_SERVICE_URL = os.getenv("EVALUATION_SERVICE_URL", "http://localhost:8003")


@router.get("/health")
def health_check():
    """Allows for services to check the health of this server if needed."""
    return {"status": "ok"}


@router.post("/visualize")
def visualize(
    chunker_config: ChunkerConfig = Body(...), document: str = Body(...)
) -> VisualizeResponse:
    """
    Receives chunking parameters and text from client, sends them to the chunking service,
    then sends the chunks to the visualization service and returns the HTML and statistics.
    """
    try:
        # Prepare the request for the chunking service
        chunking_payload: VisualizeRequest = {
            "chunker_config": chunker_config.__dict__,
            "text": normalize_document(document),
        }

        # Send request to chunking service
        chunking_response = requests.post(
            f"{CHUNKING_SERVICE_URL}/chunks", json=chunking_payload, timeout=10
        )
        chunking_response.raise_for_status()
        chunks: list[Chunk] = chunking_response.json()

        # Get chunk related stats
        stats: ChunkStatistics = calculate_chunk_stats(chunks)

        # Send chunks to visualization service
        visualization_response = requests.post(
            f"{VISUALIZATION_SERVICE_URL}/visualization", json=chunks, timeout=10
        )
        visualization_response.raise_for_status()

        # Get the text from the response
        visualization_html = visualization_response.text

        # Return dict with stats and HTML
        return {"stats": stats, "html": visualization_html}

    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid input") from exc

    except requests.RequestException as e:
        response = getattr(e, "response", None)
        if response is not None:
            if response.status_code in (400, 401, 403, 404):
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Upstream service returned a client error",
                ) from e
            else:
                raise HTTPException(
                    status_code=502, detail="Upstream service error"
                ) from e
        else:
            raise HTTPException(
                status_code=503, detail="Unable to reach upstream service"
            ) from e

    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/evaluate")
def evaluate(chunker_config: ChunkerConfig = Body(...), document: str = Body(...)):
    """
    Receives chunker configs and a text/document from the client, which it then normalizes
    and sends to the evaluation server. Once it receives a response, it gets the necessary
    data from it and sends that back to the client.
    """
    try:
        request_body = {
            "chunker_config": chunker_config.__dict__,
            "document": normalize_document(document),
        }

        # Send request to chunking service
        evaluation_response = requests.post(
            f"{EVALUATION_SERVICE_URL}/evaluate", json=request_body, timeout=120
        )
        evaluation_response.raise_for_status()
        evaluation_json = evaluation_response.json()
        metrics = {
            "omega_precision": evaluation_json["results"][0]["precision_omega_mean"],
            "precision": evaluation_json["results"][0]["precision_mean"],
            "recall": evaluation_json["results"][0]["recall_mean"],
            "iou": evaluation_json["results"][0]["iou_mean"],
        }

        return metrics

    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid input") from exc

    except requests.RequestException as e:
        response = getattr(e, "response", None)
        if response is not None:
            if response.status_code in (400, 401, 403, 404):
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Upstream service returned a client error",
                ) from e
            else:
                raise HTTPException(
                    status_code=502, detail="Upstream service error"
                ) from e
        else:
            raise HTTPException(
                status_code=503, detail="Unable to reach upstream service"
            ) from e

    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/documents")
def upload_document(document: str = Body(...)) -> DocumentPostResponse:
    """
    This endpoint receives a string and uses it to create a txt file.
    It then sends the file to S3 and returns the path/url of the created resource.
    """
    try:
        # Create a temp files
        if document:
            # Create random name
            document_name = f"{os.urandom(4).hex()}"
            document_id = f"{document_name}.txt"

            # Make sure that the directory exists
            os.makedirs("documents", exist_ok=True)
            # Track temporary file (created from the input `document` string) for cleanup
            temp_doc_path = os.path.join("documents", document_id)

            with open(temp_doc_path, "w", encoding="utf-8") as f:
                f.write(document)

        return {"document_endpoint": temp_doc_path}

    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid input") from exc

    except requests.RequestException as e:
        response = getattr(e, "response", None)
        if response is not None:
            if response.status_code in (400, 401, 403, 404):
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Upstream service returned a client error",
                ) from e
            else:
                raise HTTPException(
                    status_code=502, detail="Upstream service error"
                ) from e
        else:
            raise HTTPException(
                status_code=503, detail="Unable to reach upstream service"
            ) from e

    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


app.include_router(router, prefix="/api")
