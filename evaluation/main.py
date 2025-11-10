"""
FastAPI application for chunking evaluation.
"""

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from chromadb.utils import embedding_functions
from chunkwise_core import (
    EvaluationRequest,
    EvaluationResponse,
)
from services import evaluate

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chunkwise Evaluation API", version="1.0.0")

# Initialize embedding function - for MVP uses OpenAI embedding model by default
EMBEDDING_API_KEY = os.getenv("OPENAI_API_KEY")
if not EMBEDDING_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=EMBEDDING_API_KEY, model_name="text-embedding-3-large"
)


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_chunking(request: EvaluationRequest):
    """
    Evaluate one or more chunking strategies on a document from s3.
    """
    try:
        return await evaluate(request, embedding_func)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in evaluation pipeline")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}"
        ) from e


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "evaluation"}
