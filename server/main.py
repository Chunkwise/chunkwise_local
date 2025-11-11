"""
This is the backend server which acts as a gateway for the client to access
services and it will eventually manage the database(s) and document storage.
"""

import os
import logging
from server_types import (
    ChunkerConfig,
    VisualizeResponse,
    EvaluationMetrics,
)
from utils import (
    calculate_chunk_stats,
    delete_file,
    create_file,
    extract_metrics,
    handle_endpoint_exceptions,
    Visualizer,
)
from services import (
    upload_s3_file,
    download_s3_file,
    delete_s3_file,
    get_s3_file_names,
    get_chunks,
    get_evaluation,
)
from fastapi import FastAPI, APIRouter, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from chunkwise_core import adjustable_configs


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
async def visualize(
    document_id: str, chunker_config: ChunkerConfig = Body(...)
) -> VisualizeResponse:
    """
    Receives chunking parameters and text from client, sends them to the chunking service,
    then sends the chunks to the visualization service and returns the HTML and statistics.
    """

    await download_s3_file(document_id)

    # Make document contents into a string
    with open(f"documents/{document_id}", "r", encoding="utf8") as file:
        document = file.read()
        file.close()

    chunks = await get_chunks(chunker_config, document)
    stats = calculate_chunk_stats(chunks)
    viz = Visualizer()
    html = viz.get_html(chunks, document)

    delete_file(f"documents/{document_id}")

    # Return dict with stats and HTML
    return {"stats": stats, "html": html}


@router.get("/{document_id}/evaluation")
@handle_endpoint_exceptions
async def evaluate(
    document_id: str, chunker_config: ChunkerConfig = Body(...)
) -> list[EvaluationMetrics]:
    """
    Receives chunker configs and a document_id from the client, which it then
    sends to the evaluation server. Once it receives a response, it gets the necessary
    data from it and sends that back to the clisent.
    """

    evaluation = await get_evaluation(chunker_config, document_id)
    metrics = extract_metrics(evaluation)

    return metrics


@router.post("/")
@handle_endpoint_exceptions
async def upload_document(document: str = Body(...)) -> dict:
    """
    This endpoint receives a string and uses it to create a txt file.
    It then sends the file to S3 and returns the path/url of the created resource.
    """

    # Create a temp file
    document_id = create_file(document)
    await upload_s3_file(document_id)
    delete_file(f"documents/{document_id}")

    # Return the name of the file
    return {"document_id": document_id}


@router.get("/")
@handle_endpoint_exceptions
async def get_documents() -> list[str]:
    """
    This endpoint returns a list of all of the document_ids in s3.
    """

    # Get the list of resources from a bucket
    file_names = await get_s3_file_names()

    # Return the name of the file
    return file_names


@router.delete("/{document_id}")
@handle_endpoint_exceptions
async def delete_document(document_id: str) -> dict:
    """
    This endpoint deletes a resource from the S3 store
    """

    await delete_s3_file(document_id)

    # Return the name of the file
    return {"detail": "deleted"}


@app.exception_handler(Exception)
async def global_exception_handler(_request, _exc):
    """
    Global exception handler to ensure any unhandled exception is logged with full trace
    """
    logging.exception("Unhandled exception during request processing")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(router, prefix="/api/documents")
