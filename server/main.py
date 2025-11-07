"""
This is the backend server which acts as a gateway for the client to access
services and it will eventually manage the database(s) and document storage.
"""

import os
import requests
import logging
from server_types import (
    Chunk,
    ChunkerConfig,
    ChunkStatistics,
    VisualizeResponse,
    VisualizeRequest,
    Evaluations,
    EvaluationResponse,
)
from utils import (
    calculate_chunk_stats,
    delete_file,
    create_file,
    extract_metrics,
    handle_endpoint_exceptions,
)
from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import boto3
from botocore.exceptions import ClientError

# from chunkwise_core import adjustable_configs


app = FastAPI()
router = APIRouter()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

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
BUCKET_NAME = "chunkwise-test"


@router.get("/health")
@handle_endpoint_exceptions
def health_check() -> dict:
    """Allows for services to check the health of this server if needed."""
    return {"status": "ok"}


@router.get("/configs")
@handle_endpoint_exceptions
def configs():
    """
    Returns the adjustable parameters for each chunker's config
    """
    return adjustable_configs


@router.get("/{document_id}/visualization")
@handle_endpoint_exceptions
def visualize(
    document_id: str, chunker_config: ChunkerConfig = Body(...)
) -> VisualizeResponse:
    """
    Receives chunking parameters and text from client, sends them to the chunking service,
    then sends the chunks to the visualization service and returns the HTML and statistics.
    """

    # Download file from S3
    try:
        s3_client = boto3.client("s3")
        s3_client.download_file(BUCKET_NAME, document_id, f"documents/{document_id}")
    except ClientError as e:
        logging.exception("S3 ClientError while downloading document")

    # Make document contents into a string
    with open(f"documents/{document_id}", "r") as file:
        document = file.read()
        file.close()

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

    # Get chunk related stats
    stats = calculate_chunk_stats(chunks)

    # Send chunks to visualization service
    visualization_response = requests.post(
        f"{VISUALIZATION_SERVICE_URL}/visualize", json=chunks, timeout=10
    )
    visualization_response.raise_for_status()

    # Get the text from the response
    visualization_html = visualization_response.text

    delete_file(f"documents/{document_id}")

    # Return dict with stats and HTML
    return {"stats": stats, "html": visualization_html}


@router.get("/{document_id}/evaluation")
@handle_endpoint_exceptions
def evaluate(
    document_id: str, chunker_config: ChunkerConfig = Body(...)
) -> list[Evaluations]:
    """
    Receives chunker configs and a document_id from the client, which it then
    sends to the evaluation server. Once it receives a response, it gets the necessary
    data from it and sends that back to the clisent.
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
    metrics = extract_metrics(evaluation_json)

    return metrics


@router.post("/")
@handle_endpoint_exceptions
def upload_document(document: str = Body(...)) -> dict:
    """
    This endpoint receives a string and uses it to create a txt file.
    It then sends the file to S3 and returns the path/url of the created resource.
    """

    # Create a temp file
    document_id = create_file(document)

    # Upload the file to S3
    try:
        s3_client = boto3.client("s3")
        s3_client.upload_file(f"documents/{document_id}", BUCKET_NAME, document_id)

    except ClientError as e:
        logging.exception("S3 ClientError while uploading document")

    delete_file(f"documents/{document_id}")

    # Return the name of the file
    return {"document_id": document_id}


@router.get("/")
@handle_endpoint_exceptions
def get_documents():
    """
    This endpoint returns a list of all of the document_ids in s3.
    """

    # Get the list of resources from a bucket
    try:
        s3_client = boto3.client("s3")
        resources = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

    except ClientError as e:
        logging.exception("S3 ClientError while uploading document")

    # Create a list of the files names of a bucket
    file_names = [resource["Key"] for resource in resources["Contents"]]

    # Return the name of the file
    return file_names


@router.delete("/{document_id}")
@handle_endpoint_exceptions
def delete_document(document_id: str):
    """
    This endpoint deletes a resource from the S3 store
    """

    # Get the list of resources from a bucket
    try:
        s3_client = boto3.client("s3")
        s3_client.delete_object(Key=document_id, Bucket=BUCKET_NAME)

    except ClientError as e:
        logging.exception("S3 ClientError while uploading document")

    # Return the name of the file
    return {"detail": "deleted"}


# Global exception handler to ensure any unhandled exception is logged with full trace
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.exception("Unhandled exception during request processing")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(router, prefix="/api/documents")
