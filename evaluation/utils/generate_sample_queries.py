from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.synthetic_evaluation import (
    SyntheticEvaluation,
)
from chunkwise_core import QueryGenerationConfig


def generate_sample_queries(
    openai_api_key: str,
    document_path: str,
    corpus_id: str,
    queries_output_path: str,
    query_generation_config: QueryGenerationConfig = QueryGenerationConfig(),
) -> str:
    """
    Generate synthetic queries and reference excerpts for evaluation using LLM.

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
