"""
This is the backend server which acts as a gateway for the client to access
services and it will eventually manage the database(s) and document storage.
"""

import os
import json
import traceback
import re
import logging
from server_types import (
    VisualizeResponse,
    EvaluationResponse,
    EvaluationMetrics,
    Workflow,
    DeployRequest,
)
from utils import (
    calculate_chunk_stats,
    delete_file,
    create_file,
    extract_metrics,
    handle_endpoint_exceptions,
    Visualizer,
    adjustable_configs,
    secret_name_for_instance,
    sse_event,
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
    create_preprovisioned_instance_if_missing,
    describe_instance,
    ensure_secret,
    get_secret,
    connect_db,
    ensure_pgvector_and_table,
)
from fastapi import FastAPI, APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

app = FastAPI()
router = APIRouter()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# Configuration for RDS via env
PREPROV_DB_IDENTIFIER = os.environ.get("PREPROV_DB_IDENTIFIER", "shared-wf-db")
SHARED_DB_NAME = os.environ.get("SHARED_DB_NAME")
RDS_MASTER_USER = os.environ.get("RDS_MASTER_USER")
RDS_INSTANCE_CLASS = os.environ.get("RDS_INSTANCE_CLASS")
RDS_ENGINE_VERSION = os.environ.get("RDS_ENGINE_VERSION")
RDS_ALLOCATED_STORAGE = int(os.environ.get("RDS_ALLOCATED_STORAGE"))
RDS_PUBLIC = os.environ.get("RDS_PUBLIC", "true").lower() == "true"
RDS_WAIT_TIMEOUT = int(os.environ.get("RDS_WAIT_TIMEOUT"))
RDS_SG_IDS = os.environ.get("RDS_SG_IDS")
RDS_SG_LIST = RDS_SG_IDS.split(",") if RDS_SG_IDS else None
RDS_SUBNET_GROUP = os.environ.get("RDS_SUBNET_GROUP")
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM"))


@app.on_event("startup")
async def startup_event():
    """
    Initialize database schema on application startup, and
    ensure RDS instance and Secrets Manager secret exist.
    """
    logging.info("Initializing database schema...")
    setup_schema()
    logging.info("Database schema initialized successfully")

    # Prepare a deterministic secret name and ensure credentials exist
    secret_name = secret_name_for_instance(PREPROV_DB_IDENTIFIER)
    try:
        sec_val, sec_arn = ensure_secret(secret_name, username=RDS_MASTER_USER)
    except Exception as e:
        logging.exception(
            "Failed to ensure secret in Secrets Manager at startup: %s", e
        )
        raise

    # Creds to provision/verify instance
    master_password = sec_val["password"]
    master_user = sec_val["username"]

    # Create RDS instance if missing and wait for it to be available
    try:
        info = create_preprovisioned_instance_if_missing(
            db_identifier=PREPROV_DB_IDENTIFIER,
            master_username=master_user,
            master_password=master_password,
            db_name=SHARED_DB_NAME,
            engine_version=RDS_ENGINE_VERSION,
            db_instance_class=RDS_INSTANCE_CLASS,
            allocated_storage=RDS_ALLOCATED_STORAGE,
            vpc_security_group_ids=RDS_SG_LIST,
            db_subnet_group_name=RDS_SUBNET_GROUP,
            publicly_accessible=RDS_PUBLIC,
            wait_timeout=RDS_WAIT_TIMEOUT,
        )
    except Exception as e:
        logging.exception("Failed to create/wait for RDS instance at startup: %s", e)
        raise

    # Quick check to see if we can connect to the DB
    try:
        connection = connect_db(
            host=info["address"],
            port=info["port"],
            user=master_user,
            password=master_password,
            dbname=SHARED_DB_NAME,
        )
        connection.close()
    except Exception as e:
        logging.exception("Failed DB connection: %s", e)
        raise

    logging.info(
        "Startup: RDS instance %s available at %s:%s; secret ARN: %s",
        PREPROV_DB_IDENTIFIER,
        info["address"],
        info["port"],
        sec_arn,
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


@router.post("/workflows/{workflow_id}/deploy")
@handle_endpoint_exceptions
def deploy_workflow_db_sse(workflow_id: int, req: DeployRequest):
    """
    SSE POST: assumes startup has provisioned the RDS instance and Secrets Manager secret.
    Streams: rds-ready (with secret ARN), s3-connected (or s3-error), done.
    """

    def event_generator():
        # Ensure instance is available and get endpoint
        try:
            info = describe_instance(PREPROV_DB_IDENTIFIER)
            address = info["address"]
            port = info["port"]
        except Exception as e:
            yield sse_event(
                {"ok": False, "stage": "rds-describe", "error": str(e)}, event="error"
            )
            return

        # Get secret ARN and runtime secret
        secret_name = secret_name_for_instance(PREPROV_DB_IDENTIFIER)
        try:
            secret_json, arn = get_secret(secret_name)
            master_user = secret_json.get("username")
            master_password = secret_json.get("password")
        except Exception as e:
            yield sse_event(
                {"ok": False, "stage": "secrets-get", "error": str(e)}, event="error"
            )
            return

        # Connect and ensure table and truncate
        try:
            conn = connect_db(
                host=address,
                port=port,
                user=master_user,
                password=master_password,
                dbname=SHARED_DB_NAME,
            )
            table_name = ensure_pgvector_and_table(
                conn, workflow_id=workflow_id, embedding_dim=EMBEDDING_DIM
            )
            conn.close()
        except Exception as e:
            tb = traceback.format_exc()
            yield sse_event(
                {"ok": False, "stage": "db-setup", "error": str(e), "trace": tb},
                event="error",
            )
            return

        # Emit rds-ready with secret ARN
        rds_payload = {
            "ok": True,
            "stage": "rds-ready",
            "db_instance_identifier": PREPROV_DB_IDENTIFIER,
            "endpoint": address,
            "port": port,
            "database": SHARED_DB_NAME,
            "username_secret_arn": arn,
            "table_name": table_name,
            "notes": "The ARN references the master credentials in Secrets Manager. Grant caller IAM permission to read it if client needs credentials.",
        }
        yield sse_event(rds_payload, event="rds-ready")

        # Connect to S3 using provided credentials
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=req.s3_access_key,
                aws_secret_access_key=req.s3_secret_key,
                region_name=req.s3_region or None,
            )
            try:
                s3_client.head_bucket(Bucket=req.s3_bucket)
                yield sse_event(
                    {
                        "ok": True,
                        "stage": "s3-connected",
                        "bucket": req.s3_bucket,
                        "region": req.s3_region,
                    },
                    event="s3-connected",
                )
            except ClientError as e:
                yield sse_event(
                    {"ok": False, "stage": "s3-verify", "error": str(e)},
                    event="s3-error",
                )
                return
        except NoCredentialsError:
            yield sse_event(
                {"ok": False, "stage": "s3", "error": "invalid S3 credentials"},
                event="s3-error",
            )
            return
        except EndpointConnectionError as e:
            yield sse_event(
                {"ok": False, "stage": "s3", "error": str(e)}, event="s3-error"
            )
            return
        except Exception as e:
            yield sse_event(
                {"ok": False, "stage": "s3", "error": str(e)}, event="s3-error"
            )
            return

        yield sse_event({"ok": True, "stage": "done"}, event="done")

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.exception_handler(Exception)
async def global_exception_handler(_request, _exc):
    """
    Global exception handler to ensure any unhandled exception is logged with full trace
    """
    logging.exception("Unhandled exception during request processing")
    raise HTTPException(status_code=500, detail="Internet server error")


app.include_router(router, prefix="/api")
