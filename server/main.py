"""
This is the backend server which acts as a gateway for the client to access
services and it will eventually manage the database(s) and document storage.
"""

import os
import traceback
import re
import logging
import hashlib
import json
from server_types import (
    VisualizeResponse,
    EvaluationResponse,
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
    get_chunker_config,
    get_db_connection,
    ensure_pgvector_and_table,
)
from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_SECRET_NAME,
    VECTOR_DB_HOST,
    VECTOR_DB_PORT,
    VECTOR_DB_NAME,
    VECTOR_DB_SECRET_NAME,
    EMBEDDING_DIM,
)
from fastapi import FastAPI, APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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


def get_db_credentials(secret_name: str) -> dict:
    """
    Get database credentials from AWS Secrets Manager.

    Returns dict with keys: username, password, host, port, dbname, engine
    """
    try:
        secretsmanager = boto3.client("secretsmanager")
        secret_response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_response["SecretString"])
        return secret
    except Exception as e:
        logging.error("Failed to get secret %s: %s", secret_name, e)
        raise


@app.on_event("startup")
async def startup_event():
    """
    Initialize database schema on application startup, and
    ensure RDS instance and Secrets Manager secret exist.
    """
    logging.info("🚀 Starting Chunkwise server...")

    # Initialzing evaluaiton database schema (for experimentation workflows)
    logging.info("Initializing database schema...")
    try:
        db_creds = get_db_credentials(DB_SECRET_NAME)
        setup_schema()
        logging.info("Evaluation database schema initialized")
    except Exception as e:
        logging.exception("Failed to initialize evaluation database: %s", e)
        raise

    # Verify production database connection (for deployment workflows)
    if VECTOR_DB_HOST:
        try:
            logging.info("Verifying production database connection...")

            # Get production DB credentials from Secrets Manager
            vec_db_creds = get_db_credentials(VECTOR_DB_SECRET_NAME)

            # Extract credentials (all stored in Secrets Manager)
            db_user = vec_db_creds.get("username")
            db_password = vec_db_creds.get("password")
            db_host = vec_db_creds.get("host", VECTOR_DB_HOST)
            db_port = int(vec_db_creds.get("port", VECTOR_DB_PORT))
            db_name = vec_db_creds.get("dbname", VECTOR_DB_NAME)

            # Test connection
            with get_db_connection(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
            ) as conn:
                with conn.cursor():
                    logging.info("Connected to production vector DB")

        except Exception as e:
            logging.exception("Failed to connect to production vector database: %s", e)
            raise
    else:
        logging.warning("⚠️  VECTOR_DB_HOST not set - deploy endpoint will not work")

    logging.info("✅ Startup complete! Server ready.")


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
async def evaluate(workflow_id: int) -> EvaluationResponse:
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

    return evaluation


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
async def deploy_workflow_db_sse(workflow_id: int, req: DeployRequest):
    """
    Deploy a workflow to process, chunk, and embed documents from user's S3 bucket using AWS Batch.

    This endpoint:
    1. Creates a table in the production database for this workflow
    2. Verifies access to user's S3 bucket
    3. Submits AWS Batch jobs to process each document
    4. Streams progress via Server-Sent Events (SSE)

    Events: rds-ready, s3-connected, jobs-submitted, done
    """

    chunker_config = get_chunker_config(workflow_id)

    def event_generator():
        # Verify production DB is configured
        if not VECTOR_DB_HOST:
            yield sse_event(
                {
                    "ok": False,
                    "stage": "config",
                    "error": "Production database not configured",
                },
                event="error",
            )
            return

        # Get production vector database credentials from Secrets Manager
        try:
            prod_db_creds = get_db_credentials(VECTOR_DB_SECRET_NAME)

            # Extract all connection details from secret
            vec_db_user = prod_db_creds.get("username")
            vec_db_password = prod_db_creds.get("password")
            vec_db_host = prod_db_creds.get("host", VECTOR_DB_HOST)
            vec_db_port = int(prod_db_creds.get("port", VECTOR_DB_PORT))
            vec_db_name = prod_db_creds.get("dbname", VECTOR_DB_NAME)

            # Get secret ARN for client reference
            secretsmanager = boto3.client("secretsmanager")
            secret_response = secretsmanager.get_secret_value(
                SecretId=VECTOR_DB_SECRET_NAME
            )
            secret_arn = secret_response["ARN"]
        except Exception as e:
            yield sse_event(
                {"ok": False, "stage": "secrets-get", "error": str(e)}, event="error"
            )
            return

        # Connect to vector DB and create table for this workflow
        try:
            with get_db_connection(
                host=vec_db_host,
                port=vec_db_port,
                database=vec_db_name,
                user=vec_db_user,
                password=vec_db_password,
            ) as conn:
                table_name = ensure_pgvector_and_table(
                    conn, workflow_id=workflow_id, embedding_dim=EMBEDDING_DIM
                )
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
            "endpoint": vec_db_host,
            "port": vec_db_port,
            "database": vec_db_name,
            "user": vec_db_user,
            "password": vec_db_password,
            "table_name": table_name,
        }
        yield sse_event(rds_payload, event="rds-ready")

        # Connect to S3 using provided credentials
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=req.s3_access_key,
                aws_secret_access_key=req.s3_secret_key,
            )
            bucket = req.s3_bucket

            # Verify bucket access
            try:
                s3_client.head_bucket(Bucket=bucket)
                yield sse_event(
                    {
                        "ok": True,
                        "stage": "s3-connected",
                        "bucket": bucket,
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
                {"ok": False, "stage": "s3", "error": "Invalid S3 credentials"},
                event="s3-error",
            )
            return
        except EndpointConnectionError as e:
            yield sse_event(
                {
                    "ok": False,
                    "stage": "s3",
                    "error": f"Cannot connect to S3: {str(e)}",
                },
                event="s3-error",
            )
            return
        except Exception as e:
            yield sse_event(
                {"ok": False, "stage": "s3", "error": str(e)}, event="s3-error"
            )
            return

        # List documents in S3 bucket and submit Batch jobs
        try:
            paginator = s3_client.get_paginator("list_objects_v2")
            keys = []

            # Find all .txt and .md files
            for page in paginator.paginate(Bucket=bucket):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if key.endswith(".txt") or key.endswith(".md"):
                        keys.append(key)
            if not keys:
                yield sse_event(
                    {
                        "ok": True,
                        "stage": "no-documents",
                        "message": "No .txt or .md files found in bucket",
                    },
                    event="no-documents",
                )
                yield sse_event({"ok": True, "stage": "done"}, event="done")
                return

            # Submit AWS Batch jobs for each document
            batch_client = boto3.client("batch")
            job_ids = []

            for doc_key in keys:
                # Create safe job name from document key hash
                safe_name = hashlib.sha1(doc_key.encode()).hexdigest()[:10]

                response = batch_client.submit_job(
                    jobName=f"chunkwise-{safe_name}",
                    jobQueue="chunkwise-job-queue",
                    jobDefinition="chunkwise-job-definition",
                    containerOverrides={
                        "environment": [
                            # Document and S3 info
                            {"name": "DOCUMENT_KEY", "value": doc_key},
                            {"name": "BUCKET_NAME", "value": bucket},
                            {"name": "AWS_ACCESS_KEY_ID", "value": req.s3_access_key},
                            {
                                "name": "AWS_SECRET_ACCESS_KEY",
                                "value": req.s3_secret_key,
                            },
                            # Vector database connection info
                            {"name": "VECTOR_DB_HOST", "value": vec_db_host},
                            {"name": "VECTOR_DB_PORT", "value": str(vec_db_port)},
                            {"name": "VECTOR_DB_NAME", "value": vec_db_name},
                            {"name": "VECTOR_DB_USER", "value": vec_db_user},
                            {"name": "VECTOR_DB_PASSWORD", "value": vec_db_password},
                            {"name": "VECTOR_DB_TABLE", "value": table_name},
                            # Chunking configuration
                            {
                                "name": "CHUNKER_CONFIG",
                                "value": chunker_config.model_dump_json(),
                            },
                            # Openai API key
                            {"name": "OPENAI_API_KEY", "value": os.getenv("OPENAI_API_KEY")},
                        ]
                    },
                )
                if "jobId" not in response:
                    yield sse_event(
                        {"ok": False, "stage": "batch-submit", "error": str(response)},
                        event="batch-error",
                    )
                    return
                job_ids.append(response["jobId"])

            yield sse_event(
                {
                    "ok": True,
                    "stage": "jobs-submitted",
                    "count": len(job_ids),
                    "documents": keys,
                    "job_ids": job_ids[:10],  # Only show first 10 to avoid huge payload
                    "message": f"Submitted {len(job_ids)} jobs to AWS Batch",
                },
                event="jobs-submitted",
            )
        except Exception as e:
            yield sse_event(
                {
                    "ok": False,
                    "stage": "batch",
                    "error": str(e),
                    "trace": traceback.format_exc(),
                },
                event="batch-error",
            )
            return

        yield sse_event(
            {
                "ok": True,
                "stage": "done",
                "summary": {
                    "database": f"{vec_db_host}:{vec_db_port}/{vec_db_name}",
                    "table": table_name,
                    "documents_processed": len(job_ids),
                    "message": "Jobs submitted successfully. Monitor progress in AWS Batch console.",
                },
            },
            event="done",
        )

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.exception_handler(Exception)
async def global_exception_handler(_request, _exc):
    """
    Global exception handler to ensure any unhandled exception is logged with full trace
    """
    logging.exception("Unhandled exception during request processing")
    raise HTTPException(status_code=500, detail="Internet server error")


app.include_router(router, prefix="/api")
