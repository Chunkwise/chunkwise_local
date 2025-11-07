from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.synthetic_evaluation import (
    SyntheticEvaluation,
)
from chunkwise_core import QueryGenerationConfig


def generate_sample_queries(config: QueryGenerationConfig) -> str:
    """Generate synthetic queries and reference excerpts for evaluation."""

    try:
        # Initialize the SyntheticEvaluation class
        evaluator = SyntheticEvaluation(
            corpora_paths=config.document_paths,
            queries_csv_path=config.queries_output_path,
            chroma_db_path=config.chroma_db_path,
            openai_api_key=config.openai_api_key,
        )

        # Generate queries and excerpts
        evaluator.generate_queries_and_excerpts(
            approximate_excerpts=config.approximate_excerpts,
            num_rounds=config.num_rounds,
            queries_per_corpus=config.queries_per_corpus,
        )

        # Filters out questions where the reference excerpts don't match well
        evaluator.filter_poor_excerpts(threshold=config.poor_reference_threshold)

        # Removes questions that are too similar to each other
        evaluator.filter_duplicates(threshold=config.duplicate_question_threshold)

        return config.queries_output_path
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating queries: {str(e)}"
        ) from e
