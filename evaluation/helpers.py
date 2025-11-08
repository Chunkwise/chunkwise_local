import os
from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
from chunkwise_core import (
    create_chunker,
    QueryGenerationConfig,
    Evaluation,
    EvaluationRequest,
)
from utils import generate_sample_queries


def handle_document_input(
    document: str | None,
    document_path: str | None,
    output_dir: str,
) -> tuple[str, str, str]:
    """
    Handle document input from either path or content string.

    Args:
        document: Document content as string (for MVP/testing)
        document_path: Path to existing document file
        output_dir: Directory where temporary files will be created

    Returns:
        tuple: (document_path, document_id, document_name)
    """
    if document:
        # Create temporary file from document content (MVP mode)
        document_name = f"temp_doc_{os.urandom(4).hex()}"
        document_id = f"{document_name}.txt"

        os.makedirs(output_dir, exist_ok=True)
        temp_doc_path = os.path.join(output_dir, document_id)

        with open(temp_doc_path, "w", encoding="utf-8") as f:
            f.write(document)

        return temp_doc_path, document_id, document_name

    if document_path:
        # Validate the document path
        if not os.path.exists(document_path):
            raise HTTPException(
                status_code=404,
                detail=f"Document not found at path: {document_path}",
            )

        if not os.path.isfile(document_path):
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a file: {document_path}",
            )

        document_id = os.path.basename(document_path)
        document_name = os.path.splitext(document_id)[0]

        return document_path, document_id, document_name

    raise HTTPException(
        status_code=400,
        detail="Either 'document' or 'document_path' must be provided",
    )


def count_queries(queries_path: str) -> int | None:
    """
    Count the number of queries in a CSV file.

    Args:
        queries_path: Path to queries CSV file

    Returns:
        Number of queries (excluding header) or None if unreadable
    """
    try:
        with open(queries_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f) - 1  # Exclude header
    except (OSError, UnicodeDecodeError):
        return None


def handle_queries(
    request: EvaluationRequest, normalized_doc_path: str, document_name: str
) -> tuple[str, bool, int | None]:
    """
    Handle queries - either use existing or generate new ones via LLM.

    Args:
        request: EvaluationRequest containing query configurations
        normalized_doc_path: Path to normalized document
        document_name: Name of the document (without extension)

    Returns:
        tuple: (queries_path, queries_generated, num_queries)
    """
    if request.queries_path:
        # Use existing queries
        if not os.path.exists(request.queries_path):
            raise HTTPException(
                status_code=404,
                detail=f"Queries file not found at path: {request.queries_path}",
            )
        return request.queries_path, False, None

    # Generate queries using LLM
    llm_api_key = os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY environment variable is required for query generation",
        )

    queries_filename = f"llm_queries_{document_name}.csv"
    queries_output_path = os.path.join(request.queries_output_dir, queries_filename)

    try:
        query_generation_config = QueryGenerationConfig(
            openai_api_key=llm_api_key,
            document_paths=[normalized_doc_path],
            queries_output_path=queries_output_path,
            num_rounds=request.num_rounds,
            queries_per_corpus=request.queries_per_corpus,
            approximate_excerpts=request.approximate_excerpts,
            poor_reference_threshold=request.poor_reference_threshold,
            duplicate_question_threshold=request.duplicate_question_threshold,
        )

        final_queries_path = generate_sample_queries(query_generation_config)
        num_queries = count_queries(final_queries_path)
        if num_queries is None:
            num_queries = request.queries_per_corpus * request.num_rounds
        return final_queries_path, True, num_queries

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating sample queries: {str(e)}",
        ) from e


def run_chunker_evaluations(
    request: EvaluationRequest, evaluation: BaseEvaluation, embedding_func
) -> tuple[list[str], list[Evaluation]]:
    """
    Run evaluations for all chunking configurations.

    Args:
        request: EvaluationRequest containing chunking configs
        evaluation: Initialized BaseEvaluation instance
        embedding_func: Embedding function to use for evaluation

    Returns:
        tuple: (chunker_names, results)
    """
    results = []
    chunker_names = []

    for config in request.chunking_configs:
        try:
            chunker = create_chunker(config)
            metrics = evaluation.run(chunker, embedding_function=embedding_func)
            chunker_name = f"{config.chunker_type}"
            chunker_names.append(chunker_name)
            results.append(Evaluation(**metrics))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error evaluating chunker {config.chunker_type}: {str(e)}",
            ) from e

    return chunker_names, results
