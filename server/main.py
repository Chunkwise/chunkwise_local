"""
This is the backend server which acts as a gateway for the client to access
services and it will eventually manage the database(s) and document storage.
"""

import os
import logging
from server_types import (
    VisualizeResponse,
    EvaluationMetrics,
    Workflow,
)
from utils import (
    calculate_chunk_stats,
    delete_file,
    create_file,
    extract_metrics,
    handle_endpoint_exceptions,
    Visualizer,
    get_chunks_with_metadata,
)
from services import (
    upload_s3_file,
    download_s3_file,
    delete_s3_file,
    get_s3_file_names,
    get_evaluation,
    create_workflow,
    update_workflow,
    delete_workflow,
    get_all_workflows,
    get_chunker_configuration,
    get_document_title,
)
from fastapi import FastAPI, APIRouter, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from chunkwise_core import adjustable_configs, create_chunker


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


@router.get("/workflows/{workflow_id}/visualization")
@handle_endpoint_exceptions
async def visualize(workflow_id: int) -> VisualizeResponse:
    """
    Receives chunking parameters and text from client, sends them to the chunking service,
    then sends the chunks to the visualization service and returns the HTML and statistics.
    """

    document_title = get_document_title(workflow_id)
    chunker_config = get_chunker_configuration(workflow_id)
    await download_s3_file(document_title)

    # Make document contents into a string
    with open(f"documents/{document_title}.txt", "r", encoding="utf8") as file:
        document = file.read()
        file.close()

    chunker = create_chunker(chunker_config)
    chunks = get_chunks_with_metadata(chunker, document)
    stats = calculate_chunk_stats(chunks)
    viz = Visualizer()
    html = viz.get_html(chunks, document)

    delete_file(f"documents/{document_title}.txt")

    workflow_update = Workflow(chunks_stats=stats, visualization_html=html)
    update_workflow(workflow_id, workflow_update)

    # Return dict with stats and HTML
    return VisualizeResponse(stats=stats, html=html)


@router.get("/workflows/{workflow_id}/evaluation")
@handle_endpoint_exceptions
async def evaluate(workflow_id: int) -> list[EvaluationMetrics]:
    """
    Receives chunker configs and a document_id from the client, which it then
    sends to the evaluation server. Once it receives a response, it gets the necessary
    data from it and sends that back to the clisent.
    """

    document_title = get_document_title(workflow_id)
    chunker_config = get_chunker_configuration(workflow_id)
    evaluation = await get_evaluation(chunker_config, document_title)
    metrics = extract_metrics(evaluation)

    workflow_update = Workflow(evaluation_metrics=metrics[0])
    update_workflow(workflow_id, workflow_update)

    return metrics


@router.post("/documents")
@handle_endpoint_exceptions
async def upload_document(
    document_title: str = Body(...),
    document_content: str = Body(...),
) -> dict:
    """
    This endpoint receives a string and uses it to create a txt file.
    It then sends the file to S3.
    """

    # Create a temp file
    create_file(document_title, document_content)
    await upload_s3_file(document_title)
    delete_file(f"documents/{document_title}")

    # Return the name of the file
    return {"detail": f"Successfully uploaded {document_title}"}


@router.get("/documents")
@handle_endpoint_exceptions
async def get_documents() -> list[str]:
    """
    This endpoint returns a list of all of the document_ids in s3.
    """

    # Get the list of resources from a bucket
    file_names = await get_s3_file_names()

    # Return the name of the file
    if file_names is None:
        return []
    return file_names


@router.delete("/documents/{document_title}")
@handle_endpoint_exceptions
async def delete_document(document_title: str) -> dict:
    """
    This endpoint deletes a resource from the S3 store
    """

    await delete_s3_file(document_title)

    # Return the name of the file
    return {"detail": "deleted"}


@router.get("/workflows")
@handle_endpoint_exceptions
async def get_workflows():
    result = get_all_workflows()
    return result


@router.post("/workflows")
@handle_endpoint_exceptions
async def insert_workflow(body: dict = Body(...)):
    result = create_workflow(body["title"])
    return result


@router.put("/workflows/{workflow_id}")
@handle_endpoint_exceptions
async def change_workflow(workflow_id: int, workflow_update: Workflow = Body(...)):
    result = update_workflow(workflow_id, workflow_update)
    return result


@router.delete("/workflows/{workflow_id}")
@handle_endpoint_exceptions
async def remove_workflow(workflow_id: int):
    result = delete_workflow(workflow_id)

    if result is True:
        return {"detail": "successfully deleted workflow."}

    return JSONResponse(status_code=400, content={"detail": "Error deleting workflow"})


@app.exception_handler(Exception)
async def global_exception_handler(_request, _exc):
    """
    Global exception handler to ensure any unhandled exception is logged with full trace
    """
    logging.exception("Unhandled exception during request processing")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(router, prefix="/api")
