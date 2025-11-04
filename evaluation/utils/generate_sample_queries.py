import dotenv
import os
from typing import List, Optional
from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.synthetic_evaluation import (
    SyntheticEvaluation,
)


def generate_sample_queries(
    openai_api_key: str,  # Your OpenAI API key
    document_paths: List[str],  # List of document paths
    queries_output_path: str,  # Where to save generated queries
    chroma_db_path: Optional[str] = None,  # Optional: path to ChromaDB
    num_rounds: int = 1,  # Number of rounds to generate queries (-1 for infinite)
    queries_per_corpus: int = 5,  # Number of queries to generate per document
    approximate_excerpts: bool = False,  # Set to True for approximate reference extraction
    poor_reference_threshold: float = 0.36,  # Threshold for filtering poor references
    duplicate_question_threshold: float = 0.78,  # Threshold for filtering duplicate questions
) -> str:
    """Generate synthetic queries and reference excerpts for evaluation."""

    try:
        # Initialize the SyntheticEvaluation class
        evaluator = SyntheticEvaluation(
            corpora_paths=document_paths,
            queries_csv_path=queries_output_path,
            chroma_db_path=chroma_db_path,
            openai_api_key=openai_api_key,
        )

        # Generate queries and excerpts
        evaluator.generate_queries_and_excerpts(
            approximate_excerpts=approximate_excerpts,
            num_rounds=num_rounds,
            queries_per_corpus=queries_per_corpus,
        )

        # Filters out questions where the reference excerpts don't match well
        evaluator.filter_poor_excerpts(threshold=poor_reference_threshold)

        # Removes questions that are too similar to each other
        evaluator.filter_duplicates(threshold=duplicate_question_threshold)

        # print("Query generation and filtering complete!")
        # print(f"Results saved to: {queries_output_path}")

        return queries_output_path
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating queries: {str(e)}"
        )
