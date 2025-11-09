from pydantic import BaseModel, Field, ConfigDict
from .chunker_config import ChunkerConfig, LangChainRecursiveConfig


class QueryGenerationConfig(BaseModel):
    """
    Adjustable configurations for LLM-powered query generation.

    These settings control how synthetic queries are generated from documents
    for evaluation purposes.
    """

    num_rounds: int = Field(
        default=1,
        description="Number of rounds to generate queries",
        ge=1,
        le=3,
    )
    queries_per_corpus: int = Field(
        default=5,
        description="Number of queries to generate per document",
        ge=3,
        le=10,
    )
    approximate_excerpts: bool = Field(
        default=False, description="Set to True for approximate reference extraction"
    )
    poor_reference_threshold: float = Field(
        default=0.36,
        description="Threshold for filtering poor references",
        ge=0.0,
        le=1.0,
    )
    duplicate_question_threshold: float = Field(
        default=0.78,
        description="Threshold for filtering duplicate questions",
        ge=0.0,
        le=1.0,
    )


class GenerateQueriesRequest(BaseModel):
    """
    Request to generate queries for the input document via LLM (OpenAI by default).

    Note: kept here for use in later phases for the internal generat_queries endpoint
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    openai_api_key: str = Field(
        ...,
        description="Your OpenAI API key",
        min_length=1,
        repr=False,
        json_schema_extra={"writeOnly": True},
    )
    document_paths: list[str] = Field(
        ..., description="List of document paths", min_length=1
    )
    queries_output_path: str = Field(
        ..., description="Where to save generated queries", min_length=1
    )
    query_generation_config: QueryGenerationConfig = Field(
        default_factory=QueryGenerationConfig,
        description="Adjustable settings for query generation",
    )
    # chroma_db_path: str | None = Field(
    #     default=None, description="Optional: path to ChromaDB"
    # )


class EvaluationMetrics(BaseModel):
    """Evaluation metrics for a single chunking configuration."""

    iou_mean: float
    recall_mean: float
    precision_mean: float
    precision_omega_mean: float
    chunker_config: ChunkerConfig


class EvaluateResponse(BaseModel):
    """Response containing evaluation results for one or more chunking strategies."""

    embedding_model: str
    document_id: str
    document_path: str
    queries_path: str
    queries_generated: bool
    num_queries: int | None = None
    chunkers_evaluated: list[str]
    results: list[EvaluationMetrics]


class EvaluateRequest(BaseModel):
    """Request to evaluate one or more chunking strategies on a document."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    # Document and queries
    document_id: str = Field(
        ...,
        description="Unique identifier for the S3 document",
        min_length=1,
    )
    # Optional for local testing - use document_id in production
    document_path: str | None = Field(
        default=None,
        description="Path to the document to evaluate. Can be absolute or relative path",
        min_length=1,
    )

    queries_path: str | None = Field(
        default=None,
        description="Optional: path to queries CSV. If not provided, queries will "
        "be generated using LLM (requires OPENAI_API_KEY)",
        min_length=1,
    )

    embedding_model: str = Field(
        default="openai.text-embedding-3-large", description="Embedding model to use"
    )
    openai_api_key: str | None = Field(
        default=None,
        description="Optional: OpenAI API key, required if queries path not provided",
        repr=False,
        json_schema_extra={"writeOnly": True},
    )

    queries_output_dir: str = Field(
        default="data",
        description="Where to save generated queries (only used when generating queries)",
    )

    query_generation_config: QueryGenerationConfig | None = Field(
        default=None,
        description="Adjustable settings for LLM-powered query generation. Only"
        " used when queries_path is not provided. If not provided, default values will be used",
    )

    # A list of chunking configurations (multiple strategies)
    chunking_configs: list[ChunkerConfig] = Field(
        default_factory=lambda: [
            LangChainRecursiveConfig(
                chunk_size=512,
                chunk_overlap=0,
            )
        ],
        min_length=1,
        description="List of chunker configurations to evaluate",
    )
