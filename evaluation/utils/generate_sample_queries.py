from fastapi import HTTPException
from chunking_evaluation.evaluation_framework.synthetic_evaluation import (
    SyntheticEvaluation,
)
from chunkwise_core import QueryGenerationConfig


# class QueryGenerationConfig(BaseModel):
#     """Configuration for query generation."""

#     model_config = ConfigDict(
#         str_strip_whitespace=True,
#         validate_assignment=True,
#         frozen=False,
#     )
#     openai_api_key: str = Field(..., description="Your OpenAI API key", min_length=1)
#     document_paths: list[str] = Field(
#         ..., description="List of document paths", min_length=1
#     )
#     queries_output_path: str = Field(
#         ..., description="Where to save generated queries", min_length=1
#     )
#     chroma_db_path: str | None = Field(
#         default=None, description="Optional: path to ChromaDB"
#     )
#     num_rounds: int = Field(
#         default=1,
#         description="Number of rounds to generate queries",
#         ge=1,
#     )
#     queries_per_corpus: int = Field(
#         default=5, description="Number of queries to generate per document", gt=0
#     )
#     approximate_excerpts: bool = Field(
#         default=False, description="Set to True for approximate reference extraction"
#     )
#     poor_reference_threshold: float = Field(
#         default=0.36,
#         description="Threshold for filtering poor references",
#         ge=0.0,
#         le=1.0,
#     )
#     duplicate_question_threshold: float = Field(
#         default=0.78,
#         description="Threshold for filtering duplicate questions",
#         ge=0.0,
#         le=1.0,
#     )


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
