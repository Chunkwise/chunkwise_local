import os
import logging
import tempfile
import shutil
from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
from chunkwise_core import (
    create_chunker,
    ChunkerConfig,
    QueryGenerationConfig,
    EvaluationMetrics,
    EvaluationRequest,
)

from utils import generate_sample_queries
from s3_utils import (
    download_file,
    upload_file,
    exists,
    get_document_s3_key,
    get_queries_s3_key,
    is_s3_configured,
)

logger = logging.getLogger(__name__)


def get_canonical_corpus_id(document_id: str) -> str:
    """
    Extract canonical corpus ID from document_id.

    The canonical corpus ID is used as a stable identifier in the queries CSV,
    independent of where the file is temporarily stored (e.g., Lambda /tmp).

    Examples:
        "my_doc" -> "my_doc"
        "my_doc.txt" -> "my_doc"

    Args:
        document_id: Document identifier (with or without .txt extension)

    Returns:
        Canonical corpus ID without extension
    """
    if document_id.endswith(".txt"):
        return document_id[:-4]
    return document_id


def download_s3_queries(queries_s3_key: str) -> tuple[str, int | None] | None:
    """
    Download queries from S3 to temporary file if they exist.

    Args:
        queries_s3_key: S3 key for queries CSV

    Returns:
        Tuple of (temp_queries_path, num_queries) if found, None if not found
    """
    if not exists(queries_s3_key):
        return None

    # Create temp file for queries
    temp_queries_file = tempfile.NamedTemporaryFile(
        mode="w+b", suffix=".csv", delete=False
    )
    temp_queries_path = temp_queries_file.name
    temp_queries_file.close()

    if not download_file(queries_s3_key, temp_queries_path):
        # Clean up on failure
        try:
            os.unlink(temp_queries_path)
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download queries from S3: {queries_s3_key}",
        )

    num_queries = count_queries_in_csv(temp_queries_path)
    return temp_queries_path, num_queries


def generate_and_upload_queries(
    request: EvaluationRequest,
    temp_document_path: str,
    canonical_corpus_id: str,
    queries_s3_key: str,
) -> tuple[str, int | None]:
    """
    Generate new queries using LLM and upload to S3.

    Args:
        request: Evaluation request
        temp_document_path: Temporary path to downloaded document
        canonical_corpus_id: Canonical corpus identifier (e.g., "my_doc")
        queries_s3_key: S3 key where queries should be uploaded

    Returns:
        Tuple of (temp_queries_path, num_queries)
    """
    llm_api_key = request.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY must be provided when generating queries",
        )

    query_gen_config = request.query_generation_config or QueryGenerationConfig()

    # Create temp directory for generated queries
    queries_output_dir = tempfile.mkdtemp()
    queries_filename = f"llm_queries_{canonical_corpus_id}.csv"
    queries_output_path = os.path.join(queries_output_dir, queries_filename)

    try:
        # Generate queries
        final_queries_path = generate_sample_queries(
            openai_api_key=llm_api_key,
            document_path=temp_document_path,
            corpus_id=canonical_corpus_id,  # Use canonical ID, not temp path
            queries_output_path=queries_output_path,
            query_generation_config=query_gen_config,
        )
        num_queries = count_queries_in_csv(final_queries_path)

        if num_queries is None:
            # Fallback estimate
            num_queries = (
                query_gen_config.queries_per_corpus * query_gen_config.num_rounds
            )

        # Upload to S3
        if not upload_file(final_queries_path, queries_s3_key):
            logger.warning(
                "Failed to upload generated queries to S3: %s", queries_s3_key
            )

        return final_queries_path, num_queries

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating queries: {str(e)}",
        ) from e
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(queries_output_dir, ignore_errors=True)
        except:
            pass


def resolve_queries(
    request: EvaluationRequest,
    temp_document_path: str,
    canonical_corpus_id: str,
    document_id: str,
) -> tuple[str, bool, int | None, str]:
    """
    Resolve queries from S3 or generate new ones.

    Priority:
    1. If queries_id provided: Download those specific queries from S3
    2. If queries exist for document_id: Download and reuse them
    3. Otherwise: Generate new queries and upload to S3

    Args:
        request: Evaluation request
        temp_document_path: Temporary path to document
        canonical_corpus_id: Canonical corpus identifier
        document_id: Document identifier

    Returns:
        Tuple of (temp_queries_path, queries_generated, num_queries, queries_s3_key)
    """
    if request.queries_id:
        # Use specific queries_id
        queries_s3_key = get_queries_s3_key(request.queries_id)
        result = download_s3_queries(queries_s3_key)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Queries not found in S3 for queries_id: {request.queries_id}",
            )

        temp_queries_path, num_queries = result
        return temp_queries_path, False, num_queries, queries_s3_key

    # Try to reuse queries for this document
    queries_s3_key = get_queries_s3_key(document_id)
    result = download_s3_queries(queries_s3_key)

    if result is not None:
        # Found existing queries
        temp_queries_path, num_queries = result
        return temp_queries_path, False, num_queries, queries_s3_key

    # Generate new queries
    temp_queries_path, num_queries = generate_and_upload_queries(
        request, temp_document_path, canonical_corpus_id, queries_s3_key
    )
    return temp_queries_path, True, num_queries, queries_s3_key


def count_queries_in_csv(csv_path: str) -> int | None:
    """
    Count the number of queries in a CSV file.

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


def run_chunker_evaluations(
    evaluation: BaseEvaluation, chunking_configs: list[ChunkerConfig], embedding_func
) -> tuple[list[str], list[EvaluationMetrics]]:
    """
    Run evaluations for all chunking configurations.

    Args:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ?? Request containing chunking configs
        evaluation: Initialized BaseEvaluation instance
        chunking_configs: List of chunker configurations to evaluate
        embedding_func: Embedding function to use for evaluation

    Returns:
        tuple: (chunker_names, evaluation_results)
    """
    evaluation_results = []
    chunker_names = []

    for config in chunking_configs:
        try:
            chunker = create_chunker(config)
            metrics = evaluation.run(chunker, embedding_function=embedding_func)
            chunker_name = f"{config.provider} {config.chunker_type}"
            chunker_names.append(chunker_name)
            evaluation_results.append(EvaluationMetrics(**metrics))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error evaluating {config.provider} {config.chunker_type} chunker: {str(e)}",
            ) from e

    return chunker_names, evaluation_results
