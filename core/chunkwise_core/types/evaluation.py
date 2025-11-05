from typing import List
from pydantic import BaseModel, Field
from .chunker_config import ChunkerConfig, LangChainRecursiveConfig


class Evaluation(BaseModel):
    iou_mean: float
    recall_mean: float
    precision_mean: float
    precision_omega_mean: float
    chunker_config: ChunkerConfig


class EvaluationResponse(BaseModel):
    embedding_model: str
    document_id: str
    document_path: str
    queries_path: str
    queries_generated: bool
    num_queries: int | None = None
    chunkers_evaluated: list[str]
    results: list[Evaluation]


class EvaluationRequest(BaseModel):
    # Document and queries
    # Teporarily optional for MVP testing - remove `None` option after document storage is setup
    document_path: str | None = Field(
        default=None,
        description="Path to the document to evaluate. Can be absolute or relative path",
    )
    # `document` field is temporary for MVP testing
    document: str = Field(
        ...,
        description="Document content as a string. Use this for MVP testing. ",
    )
    queries_path: str | None = Field(
        default=None,
        description="Optional: path to queries CSV. If not provided, queries will "
        "be generated using LLM (requires OPENAI_API_KEY)",
    )

    # Models and API
    embedding_model: str = Field(
        default="openai.text-embedding-3-large", description="Embedding model to use"
    )
    openai_api_key: str | None = Field(
        default=None,
        description="Optional: OpenAI API key, required if queries path not provided",
    )

    # Query generation settings
    queries_output_dir: str = Field(
        default="data",
        description="Where to save generated queries (only used when generating queries)",
    )
    num_rounds: int = Field(
        default=1, ge=1, le=3, description="Number of rounds to generate queries"
    )
    queries_per_corpus: int = Field(
        default=5, ge=3, le=10, description="Number of queries to generate per document"
    )

    # Evaluation settings
    approximate_excerpts: bool = Field(
        default=False, description="Set to True for approximate reference extraction"
    )
    poor_reference_threshold: float = Field(
        default=0.36,
        ge=0.0,
        le=1.0,
        description="Threshold for filtering poor references",
    )
    duplicate_question_threshold: float = Field(
        default=0.78,
        ge=0.0,
        le=1.0,
        description="Threshold for filtering duplicate questions",
    )

    # A list of chunking configurations (multiple strategies)
    chunking_configs: list[ChunkerConfig] = Field(
        default_factory=lambda: [
            LangChainRecursiveConfig(
                chunk_size=512,
                chunk_overlap=0,
            )
        ],
        description="List of chunker configurations to evaluate",
    )
