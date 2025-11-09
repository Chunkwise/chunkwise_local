from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.synthetic_evaluation import (
    SyntheticEvaluation,
)
from chunkwise_core import GenerateQueriesRequest


def generate_sample_queries(request: GenerateQueriesRequest) -> str:
    """Generate synthetic queries and reference excerpts for evaluation using LLM."""

    try:

        # Initialize the SyntheticEvaluation class
        evaluator = SyntheticEvaluation(
            # Turn the input document path into a list for compatibility with the eval framework
            corpora_paths=[request.document_path],
            queries_csv_path=request.queries_output_path,
            openai_api_key=request.openai_api_key,
            # Map temp file path to canonical corpus ID
            corpus_id_override={request.document_path: request.corpus_id}
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

        return request.queries_output_path
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating queries: {str(e)}"
        ) from e
