"""
This is the backend server which acts as a gateway for the client to access
services and it will eventually manage the database(s) and document storage.
"""

import os
import re
import logging
from server_types import (
    VisualizeResponse,
    EvaluationResponse,
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
    adjustable_configs,
)
from services import (
    upload_s3_file,
    download_s3_file,
    delete_s3_file,
    get_s3_file_names,
    get_evaluation,
    get_chunks,
    setup_schema,
    create_workflow,
    update_workflow,
    delete_workflow,
    get_all_workflows,
    get_workflow_info,
)
from fastapi import FastAPI, APIRouter, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
router = APIRouter()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@app.on_event("startup")
async def startup_event():
    """Initialize database schema on application startup"""
    logging.info("Initializing database schema...")
    setup_schema()
    logging.info("Database schema initialized successfully")


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

    document_title, chunker_config = get_workflow_info(workflow_id)
    await download_s3_file(document_title)

    # Make document contents into a string
    with open(f"documents/{document_title}.txt", "r", encoding="utf8") as file:
        document = file.read()
        file.close()

    chunks = await get_chunks(chunker_config, document)
    stats = calculate_chunk_stats(chunks)
    viz = Visualizer()
    html = viz.get_html(chunks, document)

    delete_file(f"documents/{document_title}.txt")

    workflow_update = Workflow(chunks_stats=stats, visualization_html=html)
    update_workflow(workflow_id, workflow_update.model_dump())

    # Return dict with stats and HTML
    return VisualizeResponse(stats=stats, html=html)


@router.get("/workflows/{workflow_id}/evaluation")
@handle_endpoint_exceptions
async def evaluate(workflow_id: int) -> EvaluationMetrics:
    """
    Receives chunker configs and a document_id from the client, which it then
    sends to the evaluation server. Once it receives a response, it gets the necessary
    data from it and sends that back to the clisent.
    """

    document_title, chunker_config = get_workflow_info(workflow_id)
    evaluation_raw = await get_evaluation(chunker_config, document_title)
    evaluation = EvaluationResponse.model_validate(evaluation_raw)
    metrics = extract_metrics(evaluation)

    workflow_update = Workflow(evaluation_metrics=metrics[0])
    update_workflow(workflow_id, workflow_update.model_dump())

    return metrics[0]


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

    if len(document_title) == 0 or re.search(r"[^A-Za-z0-9-_() .,]", document_title):
        raise HTTPException(status_code=400, detail="Invalid document title")
    if len(document_content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Document content must have a length greater than zero",
        )

    # Create a temp file
    create_file(document_title, document_content)
    await upload_s3_file(document_title)
    delete_file(f"documents/{document_title}.txt")

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

    if len(document_title) == 0 or re.search(r"[^A-Za-z0-9-_() .,]", document_title):
        raise HTTPException(status_code=400, detail="Invalid document title")

    await delete_s3_file(document_title)

    # Return the name of the file
    return {"detail": "deleted"}


@router.get("/workflows")
@handle_endpoint_exceptions
async def get_workflows():
    """
    Returns a list of all of the workflows.
    """
    result = get_all_workflows()
    return result


@router.post("/workflows")
@handle_endpoint_exceptions
async def insert_workflow(body: dict = Body(...)):
    """
    Creates a workflow with the given title and returns it.
    """
    workflow_title = body["title"]

    if len(workflow_title) == 0 or len(workflow_title) > 50:
        raise HTTPException(status_code=400, detail="Invalid workflow title")

    result = create_workflow(workflow_title)
    return result


@router.put("/workflows/{workflow_id}")
@handle_endpoint_exceptions
async def change_workflow(workflow_id: int, workflow_update: Workflow = Body(...)):
    """
    Updates a workflow to reflect the changes made.
    """
    if workflow_id < 1:
        raise HTTPException(status_code=400, detail="Invalid workflow id")

    if (
        not workflow_update.chunking_strategy is None
        or not workflow_update.document_title is None
    ):
        workflow_update.chunks_stats = ""
        workflow_update.visualization_html = ""
        workflow_update.evaluation_metrics = ""

    update_dict = workflow_update.model_dump()

    result = update_workflow(workflow_id, update_dict)
    return result


@router.delete("/workflows/{workflow_id}")
@handle_endpoint_exceptions
async def remove_workflow(workflow_id: int):
    """
    Deletes a workflow from the database.
    """
    result = delete_workflow(workflow_id)

    if workflow_id < 1:
        raise HTTPException(status_code=400, detail="Invalid workflow id")

    if result is True:
        return {"detail": "successfully deleted workflow."}
    else:
        raise HTTPException(status_code=400, detail="Invalid workflow id")


@app.exception_handler(Exception)
async def global_exception_handler(_request, _exc):
    """
    Global exception handler to ensure any unhandled exception is logged with full trace
    """
    logging.exception("Unhandled exception during request processing")
    raise HTTPException(status_code=500, detail="Internet server error")


app.include_router(router, prefix="/api")
