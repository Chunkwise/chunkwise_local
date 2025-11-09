import os
import hashlib
from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.synthetic_evaluation import (
    SyntheticEvaluation,
)
from chunkwise_core import GenerateQueriesRequest


def generate_sample_queries(request: GenerateQueriesRequest) -> str:
    """Generate synthetic queries and reference excerpts for evaluation using LLM."""

    try:
        run_id = _make_run_id(request.document_paths)
        queries_filename = f"queries_{run_id}.csv"
        queries_output_path = os.path.join(request.queries_output_dir, queries_filename)

        # Initialize the SyntheticEvaluation class
        evaluator = SyntheticEvaluation(
            corpora_paths=request.document_paths,
            queries_csv_path=queries_output_path,
            openai_api_key=request.openai_api_key,
            # chroma_db_path=request.chroma_db_path,
        )

        # Generate queries and excerpts
        evaluator.generate_queries_and_excerpts(
            approximate_excerpts=request.query_generation_config.approximate_excerpts,
            num_rounds=request.query_generation_config.num_rounds,
            queries_per_corpus=request.query_generation_config.queries_per_corpus,
        )

        # Removes questions where the reference excerpts don't match well
        evaluator.filter_poor_excerpts(
            threshold=request.query_generation_config.poor_reference_threshold
        )

        # Removes questions that are too similar to each other
        evaluator.filter_duplicates(
            threshold=request.query_generation_config.duplicate_question_threshold
        )

        return queries_output_path
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating queries: {str(e)}"
        ) from e



def _make_run_id(corpora_paths: list[str]) -> str:
    """
    Create a deterministic short hash ID for a given list of documents paths.
    This hash ID is used in the file name of the generated queries CSV, e.g. "queries_<run_id>.csv".

    Args:
        document_paths: List of document file paths.

    Returns:
        str: A short SHA1-based hash string (12 hex chars).
    """
    # Sort paths so order doesn’t affect the hash
    normalized = sorted([p.strip() for p in corpora_paths])
    joined = "|".join(normalized).encode("utf-8")

    # Compute SHA1 hash and shorten for readability
    digest = hashlib.sha1(joined).hexdigest()
    return digest[:12]
