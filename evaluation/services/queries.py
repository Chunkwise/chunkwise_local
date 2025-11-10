"""
Query generation and resolution functions.
"""

import os
import logging
import tempfile
import shutil
from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.synthetic_evaluation import (
    SyntheticEvaluation,
)
from chunkwise_core import EvaluationRequest, QueryGenerationConfig
from .s3_utils import (
    get_queries_s3_key,
    exists,
    download_file_temp,
    upload_file,
)


logger = logging.getLogger(__name__)


async def resolve_queries(
    request: EvaluationRequest, temp_document_path: str, canonical_corpus_id: str
) -> tuple[str, bool, int | None, str]:
    """
    Resolve queries from S3 or generate new ones.

    Workflow:
    1. If queries_id is provided: Download the specified queries CSV file (return 404 if not found)
    2. If queries CSV file exists for document_id: Reuse it
    3. Otherwise: Generate new queries and upload a CSV file to S3

    Args:
        request: Evaluation request
        temp_document_path: Temporary path to document
        canonical_corpus_id: Canonical corpus identifier

    Returns:
        Tuple of (temp_queries_path, queries_generated, num_queries, queries_s3_key)

    Raises:
        HTTPException: If queries_id specified but not found, or if download/generation fails
    """
    # User specified queries_id
    if request.queries_id:
        queries_s3_key = get_queries_s3_key(request.queries_id)

        if not exists(queries_s3_key):
            raise HTTPException(
                status_code=404,
                detail=f"Queries not found in S3 for queries_id: {request.queries_id}",
            )

        return _download_queries(queries_s3_key)

    # Check if queries exist for this document
    queries_s3_key = get_queries_s3_key(request.document_id)

    if exists(queries_s3_key):
        return _download_queries(queries_s3_key)

    # Generate new queries
    return await _handle_query_generation(
        request, temp_document_path, canonical_corpus_id, queries_s3_key
    )


def _count_queries_in_csv(csv_path: str) -> int | None:
    """

    Args:
        queries_path: Path to queries CSV file

    Returns:
        Number of queries (excluding header) or None if counting fails
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f) - 1  # Exclude header
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Failed to count queries in %s: %s", csv_path, e)
        return None


def _download_queries(queries_s3_key: str) -> tuple[str, bool, int | None, str]:
    """Download queries from S3 to temp file."""
    with download_file_temp(queries_s3_key, suffix=".csv") as temp_queries_path:
        if temp_queries_path is None:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download queries from S3: {queries_s3_key}",
            )
        
        # Count queries while we have the file
        num_queries = _count_queries_in_csv(temp_queries_path)
        
        # Copy to a new temp file that won't be auto-deleted
        new_temp_file = tempfile.NamedTemporaryFile(mode="w+b", suffix=".csv", delete=False)
        new_temp_path = new_temp_file.name
        new_temp_file.close()
        
        # Copy the contents
        shutil.copy2(temp_queries_path, new_temp_path)
        
        return new_temp_path, False, num_queries, queries_s3_key


def _generate_sample_queries(
    openai_api_key: str,
    document_path: str,
    corpus_id: str,
    queries_output_path: str,
    query_generation_config: QueryGenerationConfig = QueryGenerationConfig(),
) -> str:
    """
    A wrapper around `SyntheticEvaluation` that generates a CSV of queries and
    ground-truth excerpts for a single document.

    Args:
        openai_api_key: OpenAI API key.
        document_path: Path to the document to evaluate.
        corpus_id: Corpus ID for the document.
        queries_output_path: Path to save the generated queries CSV.
        query_generation_config: Configuration for query generation.

    Returns:
        Path to the generated queries CSV file.
    """

    try:

        # Initialize the SyntheticEvaluation class
        evaluator = SyntheticEvaluation(
            # Turn the input document path into a list for compatibility with the eval framework
            corpora_paths=[document_path],
            queries_csv_path=queries_output_path,
            openai_api_key=openai_api_key,
            # Map temp file path to canonical corpus ID
            corpus_id_override={document_path: corpus_id},
            # chroma_db_path=chroma_db_path,
        )

        # Generate queries and excerpts
        evaluator.generate_queries_and_excerpts(
            approximate_excerpts=query_generation_config.approximate_excerpts,
            num_rounds=query_generation_config.num_rounds,
            queries_per_corpus=query_generation_config.queries_per_corpus,
        )

        # Removes questions where the reference excerpts don't match well
        evaluator.filter_poor_excerpts(
            threshold=query_generation_config.poor_reference_threshold
        )

        # Removes questions that are too similar to each other
        evaluator.filter_duplicates(
            threshold=query_generation_config.duplicate_question_threshold
        )

        return queries_output_path
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating queries: {str(e)}"
        ) from e


async def _handle_query_generation(
    request: EvaluationRequest,
    temp_document_path: str,
    canonical_corpus_id: str,
    queries_s3_key: str,
) -> tuple[str, bool, int | None, str]:
    """Generate new queries using LLM and upload to S3."""
    llm_api_key = request.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        raise HTTPException(
            status_code=400, detail="OPENAI_API_KEY required when generating queries"
        )

    query_gen_config = request.query_generation_config or QueryGenerationConfig()

    queries_output_dir = tempfile.mkdtemp()
    queries_filename = f"llm_queries_{canonical_corpus_id}.csv"
    queries_output_path = os.path.join(queries_output_dir, queries_filename)

    final_queries_path = _generate_sample_queries(
        openai_api_key=llm_api_key,
        document_path=temp_document_path,
        corpus_id=canonical_corpus_id,
        queries_output_path=queries_output_path,
        query_generation_config=query_gen_config,
    )

    num_queries = _count_queries_in_csv(final_queries_path)
    if num_queries is None:
        num_queries = (
            query_gen_config.queries_per_corpus * query_gen_config.num_rounds
        )

    if not upload_file(final_queries_path, queries_s3_key):
        logger.warning("Failed to upload queries to S3: %s", queries_s3_key)

    return final_queries_path, True, num_queries, queries_s3_key

