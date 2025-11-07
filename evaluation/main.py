import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
from chromadb.utils import embedding_functions
from utils import normalize_document
from chunkwise_core import (
    EvaluationRequest,
    EvaluationResponse,
)
from helpers import handle_document_input, handle_queries, run_chunker_evaluations

load_dotenv()

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
    Evaluate one or more chunking strategies on a document using preexisting or
    LLM-generated queries.

    This endpoint performs a complete evaluation workflow:
    1. Accepts a document (via path or raw content), which is then normalized
    and written as `<document_name>_normalized.txt`
    2. Uses existing queries or generate them via the LLM for evaluation.
      Queries generated are written to `llm_queries_<document_name>.csv` in `queries_output_dir`.
    3. Tests one or multiple chunking strategies by constructing chunkers from
      `chunking_configs` and running evaluation using the configured embedding function/model.
    4. Returns detailed metrics for each chunking strategy

    Args:
        request: EvaluationRequest containing document, queries (optional), and
        chunking configurations

    Returns:
        EvaluationResponse with metrics (IoU, recall, precision, precision_omega)
        for each chunking strategy

    Raises:
        HTTPException (400): Invalid request parameters or missing required fields
        HTTPException (404): Document or queries file not found at specified path
        HTTPException (500): Error during query generation, evaluation, or processing
    """
    try:
        # Handle document input as either a path or a string
        document_path, document_id, document_name = handle_document_input(
            document=request.document,
            document_path=request.document_path,
            output_dir=request.queries_output_dir,
        )

        # Normalize the document (for extra validation in production)
        os.makedirs(request.queries_output_dir, exist_ok=True)
        normalized_doc_path = normalize_document(
            document_path,  # using generated document path created for the input string
            os.path.join(request.queries_output_dir, f"{document_name}_normalized.txt"),
        )

        # Handle queries (use existing or generate)
        final_queries_path, queries_generated, num_queries = handle_queries(
            request, normalized_doc_path, document_name
        )

        # Initialize evaluation
        try:
            evaluation = BaseEvaluation(
                questions_csv_path=final_queries_path,
                corpora_id_paths={normalized_doc_path: normalized_doc_path},
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error initializing BaseEvaluation: {e}"
            ) from e

        # Run evaluations for all chunking configs
        chunker_names, results = run_chunker_evaluations(
            request, evaluation, embedding_func
        )

        # Return response
        return EvaluationResponse(
            embedding_model="text-embedding-3-large",
            document_id=document_id,
            document_path=document_path,
            queries_path=final_queries_path,
            queries_generated=queries_generated,
            num_queries=num_queries,
            chunkers_evaluated=chunker_names,
            results=results,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error in evaluation pipeline: {str(e)}"
        ) from e


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "evaluation"}
