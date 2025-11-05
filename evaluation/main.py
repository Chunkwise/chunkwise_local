from dotenv import load_dotenv
import os
from fastapi import FastAPI, Body, HTTPException
from typing import List, Literal, Optional, Union, Callable, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_serializer
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
from chromadb.utils import embedding_functions
from chonkie.chunker.token import TokenChunker
from chonkie.chunker.recursive import RecursiveChunker
from chonkie.types import RecursiveRules
from chonkie.tokenizer import TokenizerProtocol
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from utils import normalize_document, generate_sample_queries

load_dotenv()

app = FastAPI()

EMBEDDING_API_KEY = os.getenv("OPENAI_API_KEY")

# Create an embedding function (using OpenAI as an example)
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=EMBEDDING_API_KEY, model_name="text-embedding-3-large"
)


# ChunkerConfig models using Pydantic v2
# Only considering 4 chunkers for now
class LangChainBaseChunkerConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    provider: Literal["langchain"] = "langchain"
    chunk_size: int = Field(default=4000, ge=1)
    chunk_overlap: int = Field(default=200, ge=0)
    length_function: Callable[[str], int] = len
    keep_separator: bool | Literal["start", "end"] = False
    add_start_index: bool = False
    strip_whitespace: bool = True

    @model_validator(mode="after")
    def validate_overlap(self) -> "LangChainBaseChunkerConfig":
        """Validate that chunk_overlap < chunk_size."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than "
                f"chunk_size ({self.chunk_size})"
            )
        return self

    @field_serializer("length_function")
    def _serialize_length_fn(self, fn):
        return getattr(fn, "__name__", "<callable>")


class LangChainRecursiveConfig(LangChainBaseChunkerConfig):
    chunker_type: Literal["langchain_recursive"] = "langchain_recursive"
    separators: list[str] | None = None
    keep_separator: bool | Literal["start", "end"] = True
    is_separator_regex: bool = False


class LangChainTokenConfig(BaseModel):  # doesn't use all properties on base chunker
    model_config = ConfigDict(arbitrary_types_allowed=True)
    provider: Literal["langchain"] = "langchain"
    chunker_type: Literal["langchain_token"] = "langchain_token"

    # Only relevant fields for token splitting
    chunk_size: int = Field(default=4000, ge=1)
    chunk_overlap: int = Field(default=200, ge=0)
    encoding_name: str = "gpt2"
    model_name: str | None = None
    allowed_special: Literal["all"] | set[str] = Field(default_factory=set)
    disallowed_special: Literal["all"] | set[str] = "all"


class ChonkieBaseChunkerConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    provider: Literal["chonkie"] = "chonkie"
    tokenizer: Literal["character", "word", "gpt2"] | str = "gpt2"


class ChonkieRecursiveConfig(ChonkieBaseChunkerConfig):
    chunker_type: Literal["chonkie_recursive"] = "chonkie_recursive"
    chunk_size: int = Field(default=2048, gt=0)
    tokenizer: Literal["character", "word", "gpt2"] | str = "character"
    rules: RecursiveRules = Field(default_factory=RecursiveRules)
    min_characters_per_chunk: int = Field(default=24, gt=0)


class ChonkieTokenConfig(ChonkieBaseChunkerConfig):
    chunker_type: Literal["chonkie_token"] = "chonkie_token"
    chunk_size: int = Field(default=2048, gt=0)
    chunk_overlap: int | float = Field(default=0, ge=0)
    tokenizer: Literal["character", "word", "gpt2"] | str = "character"

    @model_validator(mode="after")
    def validate_overlap(self) -> "ChonkieTokenConfig":
        if (
            isinstance(self.chunk_overlap, int)
            and self.chunk_overlap >= self.chunk_size
        ):
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than chunk_size ({self.chunk_size})"
            )
        if isinstance(self.chunk_overlap, float) and not (0 <= self.chunk_overlap < 1):
            raise ValueError(
                f"float chunk_overlap ({self.chunk_overlap}) should be a proportion in [0, 1)."
            )
        return self


ChunkerConfig = Annotated[
    Union[
        LangChainRecursiveConfig,
        LangChainTokenConfig,
        ChonkieRecursiveConfig,
        ChonkieTokenConfig,
    ],
    Field(discriminator="chunker_type"),
]


class ChunkingResult(BaseModel):
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
    results: list[ChunkingResult]


def create_chunker_from_config(
    config: ChunkerConfig,
) -> Any:
    match config:
        case LangChainRecursiveConfig():
            return RecursiveCharacterTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                length_function=config.length_function,
                keep_separator=config.keep_separator,
                add_start_index=config.add_start_index,
                strip_whitespace=config.strip_whitespace,
                separators=config.separators,
                is_separator_regex=config.is_separator_regex,
            )
        case LangChainTokenConfig():
            return TokenTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                encoding_name=config.encoding_name,
                model_name=config.model_name,
                allowed_special=config.allowed_special,
                disallowed_special=config.disallowed_special,
            )
        case ChonkieRecursiveConfig():
            return RecursiveChunker(
                tokenizer=config.tokenizer,
                chunk_size=config.chunk_size,
                rules=config.rules,
                min_characters_per_chunk=config.min_characters_per_chunk,
            )
        case ChonkieTokenConfig():
            return TokenChunker(
                tokenizer=config.tokenizer,
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
            )
        case _:
            raise ValueError(f"Invalid chunker configuration: {type(config)}")


# Note: use this when returning/printing configs
# config = config.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)


class EvaluationRequest(BaseModel):
    # Document and queries
    document_path: str = Field(
        ...,
        description="Path to the document to evaluate. Can be absolute or relative path",
    )
    queries_path: str | None = Field(
        default=None,
        description="Optional: path to queries CSV. If not provided, queries will be generated using LLM (requires OPENAI_API_KEY)",
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


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_chunking(request: EvaluationRequest):
    queries_generated = False
    final_queries_path = None
    num_queries_generated = None

    try:
        # Validate the document path
        if not os.path.exists(request.document_path):
            raise HTTPException(
                status_code=404,
                detail=f"Document not found at path: {request.document_path}",
            )

        # Check if file is readable
        if not os.path.isfile(request.document_path):
            raise HTTPException(
                status_code=400, detail=f"Path is not a file: {request.document_path}"
            )

        # Extract document ID from path
        document_id = os.path.basename(request.document_path)
        # Remove file extension for document name
        document_name = os.path.splitext(document_id)[0]

        # Normalize the document
        os.makedirs(
            request.queries_output_dir, exist_ok=True
        )  # Make sure output dir exists
        normalized_doc_path = normalize_document(
            request.document_path,
            os.path.join(request.queries_output_dir, f"{document_name}_normalized.txt"),
        )

        if request.queries_path:
            # Use existing queries
            if not os.path.exists(request.queries_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Queries file not found at path: {request.queries_path}",
                )
            final_queries_path = request.queries_path
            queries_generated = False
            num_queries_generated = None
        else:
            # Generate queries using LLM
            LLM_API_KEY = os.getenv("OPENAI_API_KEY")
            if not LLM_API_KEY:
                raise HTTPException(
                    status_code=500,
                    detail="OPENAI_API_KEY environment variable is required for query generation",
                )

            # Determine output path for generated queries
            queries_filename = f"llm_queries_{document_name}.csv"
            queries_output_path = os.path.join(
                request.queries_output_dir, queries_filename
            )

            try:
                final_queries_path = generate_sample_queries(
                    openai_api_key=LLM_API_KEY,
                    document_paths=[normalized_doc_path],
                    queries_output_path=queries_output_path,
                    num_rounds=request.num_rounds,
                    queries_per_corpus=request.queries_per_corpus,
                    approximate_excerpts=request.approximate_excerpts,
                    poor_reference_threshold=request.poor_reference_threshold,
                    duplicate_question_threshold=request.duplicate_question_threshold,
                )
                queries_generated = True
                # Count number of queries generated
                try:
                    with open(final_queries_path, "r") as f:
                        num_queries_generated = sum(1 for _ in f) - 1  # Exclude header
                except Exception:
                    num_queries_generated = (
                        request.queries_per_corpus * request.num_rounds
                    )

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generating sample queries: {str(e)}",
                )

        try:
            # Initialize BaseEvaluation using normalized document and provided queries path
            evaluation = BaseEvaluation(
                questions_csv_path=final_queries_path,
                corpora_id_paths={normalized_doc_path: normalized_doc_path},
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error initializing BaseEvaluation: {str(e)}"
            )

        results = []
        chunker_names = []

        for config in request.chunking_configs:
            try:
                chunker = create_chunker_from_config(config)
                metrics = evaluation.run(chunker, embedding_function=embedding_func)
                chunker_name = f"{config.chunker_type}"
                chunker_names.append(chunker_name)
                results.append(ChunkingResult(**metrics, chunker_config=config))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error evaluating chunker {config.chunker_type}: {str(e)}",
                )

        return EvaluationResponse(
            embedding_model="text-embedding-3-large",
            document_id=document_id,
            document_path=request.document_path,
            queries_path=final_queries_path,
            queries_generated=queries_generated,
            num_queries=num_queries_generated,
            chunkers_evaluated=chunker_names,
            results=results,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=500, detail=f"Unexpected error in evaluation pipeline: {str(e)}"
        )
