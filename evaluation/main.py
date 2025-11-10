import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
from chromadb.utils import embedding_functions
from chunkwise_core import (
    EvaluationRequest,
    EvaluationResponse,
)
from helpers import (
    get_canonical_corpus_id,
    resolve_queries,
    run_chunker_evaluations,
)
from s3_utils import download_file_temp, get_document_s3_key, exists

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize embedding function - for MVP uses OpenAI embedding model by default
EMBEDDING_API_KEY = os.getenv("OPENAI_API_KEY")
if not EMBEDDING_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=EMBEDDING_API_KEY, model_name="text-embedding-3-large"
)

# Note for future stages: use this when returning/printing configs
# config = config.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_chunking(request: EvaluationRequest):
    """
    Evaluate one or more chunking strategies on a document from s3 using preexisting or
    LLM-generated queries.

    Process:
    1. Downloads document from S3 to temporary storage (Lambda /tmp compatible)
    2. Resolves queries:
       - If queries_id provided: downloads those specific queries
       - If queries exist for document_id: reuses them
       - Otherwise: generates new queries and uploads to S3
    3. Runs evaluation for all chunking configurations
    4. Returns metrics for comparison

    All temporary files are automatically cleaned up after evaluation.
    """
    temp_queries_path = None

    try:
        # Extract canonical corpus ID from document_id
        canonical_corpus_id = get_canonical_corpus_id(request.document_id)

        # Get S3 key for document
        document_s3_key = get_document_s3_key(request.document_id)

        # Validate document exists in S3
        if not exists(document_s3_key):
            raise HTTPException(
                status_code=404,
                detail=f"Document not found in S3: {document_s3_key}",
            )

        # Download document from S3 to temporary location
        # This works in Lambda (/tmp) and local development
        with download_file_temp(document_s3_key, suffix=".txt") as temp_doc_path:
            if temp_doc_path is None:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to download document from S3: {document_s3_key}",
                )

            # Resolve queries (download from S3 or generate)
            temp_queries_path, queries_generated, num_queries, queries_s3_key = (
                resolve_queries(
                    request, temp_doc_path, canonical_corpus_id, request.document_id
                )
            )

            # Initialize evaluation
            try:
                evaluation = BaseEvaluation(
                    questions_csv_path=temp_queries_path,
                    corpora_id_paths={canonical_corpus_id: temp_doc_path},
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error initializing BaseEvaluation: {e}"
                ) from e

            # Run evaluations for all chunking configs
            chunker_names, evaluation_results = run_chunker_evaluations(
                evaluation, request.chunking_configs, embedding_func
            )

        # Return response
        return EvaluationResponse(
            embedding_model=request.embedding_model,
            corpus_id=canonical_corpus_id,
            document_s3_key=document_s3_key,
            queries_s3_key=queries_s3_key,
            queries_generated=queries_generated,
            num_queries=num_queries,
            chunkers_evaluated=chunker_names,
            results=evaluation_results,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error in evaluation pipeline: {str(e)}"
        ) from e

    finally:
        # Clean up temporary queries file if it exists
        if temp_queries_path and os.path.exists(temp_queries_path):
            try:
                os.unlink(temp_queries_path)
            except Exception as e:
                logger.warning("Failed to clean up temp queries file: %s", e)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "evaluation"}
