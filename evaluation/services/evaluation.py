"""
Core evaluation functions.
"""

import os
import logging
from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
from chunkwise_core import (
    create_chunker,
    EvaluationRequest,
    EvaluationResponse,
    EvaluationMetrics,
)
from .s3_utils import get_document_s3_key, download_file_temp, exists
from .queries import resolve_queries


logger = logging.getLogger(__name__)


async def evaluate(request: EvaluationRequest, embedding_func) -> EvaluationResponse:
    """
    Run evaluation for the given request.

    Args:
        request: Evaluation request containing document_id and configs
        embedding_func: Embedding function to use

    Returns:
        EvaluationResponse with metrics for each chunking strategy
    """
    temp_queries_path = None
    temp_doc_path = None

    try:
        # Get canonical corpus ID
        canonical_corpus_id = get_canonical_corpus_id(request.document_id)

        # Get S3 key for document
        document_s3_key = get_document_s3_key(request.document_id)

        # Validate document exists
        if not exists(document_s3_key):
            raise HTTPException(
                status_code=404, detail=f"Document not found in S3: {document_s3_key}"
            )

        # Download document - keep it for the entire evaluation
        with download_file_temp(
            document_s3_key, suffix=".txt", delete=False
        ) as temp_doc_path:
            if temp_doc_path is None:
                raise HTTPException(
                    status_code=500, detail="Failed to download document from S3"
                )

            # Resolve queries
            temp_queries_path, queries_generated, num_queries, queries_s3_key = (
                await resolve_queries(request, temp_doc_path, canonical_corpus_id)
            )

            # Initialize evaluation
            evaluation = BaseEvaluation(
                questions_csv_path=temp_queries_path,
                corpora_id_paths={canonical_corpus_id: temp_doc_path},
            )

            # Run evaluations
            chunker_names, results = run_evaluations(
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
            results=results,
        )

    finally:
        # Cleanup temp files
        if temp_doc_path and os.path.exists(temp_doc_path):
            try:
                os.unlink(temp_doc_path)
            except Exception as e:
                logger.warning("Failed to clean up temp document: %s", e)

        if temp_queries_path and os.path.exists(temp_queries_path):
            try:
                os.unlink(temp_queries_path)
            except Exception as e:
                logger.warning("Failed to clean up temp queries: %s", e)


def run_evaluations(
    evaluation: BaseEvaluation, chunking_configs: list, embedding_func
) -> tuple[list[str], list[EvaluationMetrics]]:
    """Run evaluation for all chunking configurations."""
    results = []
    chunker_names = []

    for config in chunking_configs:
        try:
            chunker = create_chunker(config)
            metrics = evaluation.run(chunker, embedding_function=embedding_func)
            chunker_name = f"{config.provider} {config.chunker_type}"
            chunker_names.append(chunker_name)
            results.append(EvaluationMetrics(**metrics))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error evaluating {config.provider} {config.chunker_type} chunker: {str(e)}",
            ) from e

    return chunker_names, results


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
