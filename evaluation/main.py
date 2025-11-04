from dotenv import load_dotenv
import os
import tempfile
import shutil
from fastapi import FastAPI, Body, HTTPException
from typing import List, Literal, Optional, Union, Callable, Any
from pydantic import BaseModel, Field, ConfigDict
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
import chromadb.utils.embedding_functions as embedding_functions
from chonkie.chunker.token import TokenChunker
from chonkie.chunker.recursive import RecursiveChunker
from chonkie.types import RecursiveRules
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from utils import normalize_document, generate_sample_queries

load_dotenv()

app = FastAPI()

EMBEDDING_API_KEY = os.getenv("OPENAI_API_KEY")

# Create an embedding function (using OpenAI as an example)
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=EMBEDDING_API_KEY, model_name="text-embedding-3-large"
)


# only considering 4 chunkers for now
class BaseChunkerConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # Required for Callable
    # For both LangChain and Chonkie chunkers
    provider: Literal["langchain", "chonkie"]
    chunk_size: int = Field(default=512, ge=1)
    # For Chonkie chunkers
    tokenizer: Union[Literal["character", "word", "gpt2"], Any] = "character"
    # For both LangChain chunkers
    length_function: Optional[Callable[[str], int]] = None
    keep_separator: Union[bool, Literal["start", "end"]] = False
    add_start_index: bool = False
    strip_whitespace: bool = True


class RecursiveChunkerConfig(BaseChunkerConfig):
    chunker_type: Literal["recursive"] = "recursive"
    # For LangChain recursive chunker (not exhaustive)
    chunk_overlap: int = Field(default=0, ge=0)
    separators: List[str] = ["\n\n", "\n", " ", ""]
    is_separator_regex: bool = False
    # For Chonkie recursive chunker
    rules: RecursiveRules = RecursiveRules()
    min_characters_per_chunk: int = 24


class TokenChunkerConfig(BaseChunkerConfig):
    chunker_type: Literal["token"] = "token"
    chunk_overlap: int = Field(default=0, ge=0)
    # For LangChain token chunker
    lang: str = "en"


class ChunkingResult(BaseModel):
    iou_mean: float
    recall_mean: float
    precision_mean: float
    precision_omega_mean: float
    chunker_config: Union[RecursiveChunkerConfig, TokenChunkerConfig]


class EvaluateResponse(BaseModel):
    embedding_model: str
    document_path: str
    queries_path: str
    queries_generated: bool
    num_queries: Optional[int] = None
    chunkers_evaluated: List[str]
    results: List[ChunkingResult]


def create_chunker_from_config(
    config: Union[RecursiveChunkerConfig, TokenChunkerConfig],
) -> Any:
    if config.provider == "langchain":
        match config.chunker_type:
            case "recursive":
                return RecursiveCharacterTextSplitter(
                    chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
                )
            case "token":
                return TokenTextSplitter(
                    chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
                )
    elif config.provider == "chonkie":
        match config.chunker_type:
            case "recursive":
                return RecursiveChunker(
                    tokenizer=config.tokenizer,
                    chunk_size=config.chunk_size,
                    rules=RecursiveRules(),
                    min_characters_per_chunk=config.min_characters_per_chunk,
                )
            case "token":
                return TokenChunker(
                    chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
                )
    raise ValueError("Invalid chunker configuration")


@app.post("/evaluate")
async def evaluate_chunking(
    document_path: str = Body(
        ...
    ),  # Path to the document to evaluate. Can be absolute or relative path
    queries_path: Optional[str] = Body(
        default=None
    ),  # Optional: path to queries CSV. If not provided, queries will be generated using LLM (requires OPENAI_API_KEY).
    embedding_model: str = Body(
        default="openai.text-embedding-3-large"
    ),  # Embedding model to use (default: openai.text-embedding-3-large)
    openai_api_key: Optional[str] = Body(
        default=None
    ),  # Optional: OpenAI API key. If not provided, queries will be generated using LLM (requires OPENAI_API_KEY).
    queries_output_dir: str = Body(
        default="data"
    ),  # Where to save generated queries (only used when generating queries)
    chroma_db_path: Optional[str] = Body(default=None),  # Optional: path to ChromaDB
    num_rounds: int = Body(
        default=1, ge=1, le=3
    ),  # Number of rounds to generate queries (-1 for infinite)
    queries_per_corpus: int = Body(
        default=5, ge=3, le=10
    ),  # Number of queries to generate per document
    approximate_excerpts: bool = Body(
        default=False
    ),  # Set to True for approximate reference extraction
    poor_reference_threshold: float = Body(
        default=0.36, ge=0.0, le=1.0
    ),  # Threshold for filtering poor references
    duplicate_question_threshold: float = Body(
        default=0.78, ge=0.0, le=1.0
    ),  # Threshold for filtering duplicate questions
    chunking_configs: List[Union[RecursiveChunkerConfig, TokenChunkerConfig]] = Body(
        default=[
            RecursiveChunkerConfig(
                chunker_type="recursive",
                provider="langchain",
                chunk_size=512,
                chunk_overlap=0,
            ),
        ],
    ),
):

    queries_generated = False
    final_queries_path = None
    num_queries_generated = None

    try:
        # Validate the document path
        if not os.path.exists(document_path):
            raise HTTPException(
                status_code=404, detail=f"Document not found at path: {document_path}"
            )

        # Check if file is readable
        if not os.path.isfile(document_path):
            raise HTTPException(
                status_code=400, detail=f"Path is not a file: {document_path}"
            )

        # Extract document ID from path
        document_id = os.path.basename(document_path)
        # Remove file extension for document name
        document_name = os.path.splitext(document_id)[0]

        # Normalize the document
        os.makedirs(queries_output_dir, exist_ok=True)
        normalized_doc_path = normalize_document(
            document_path,
            os.path.join(queries_output_dir, f"{document_name}_normalized.txt"),
        )

        if queries_path:
            # Use existing queries
            if not os.path.exists(queries_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Queries file not found at path: {queries_path}",
                )
            final_queries_path = queries_path
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
            queries_output_path = os.path.join(queries_output_dir, queries_filename)

            try:
                final_queries_path = generate_sample_queries(
                    openai_api_key=LLM_API_KEY,
                    document_paths=[normalized_doc_path],
                    queries_output_path=queries_output_path,
                    chroma_db_path=chroma_db_path,
                    num_rounds=num_rounds,
                    queries_per_corpus=queries_per_corpus,
                    approximate_excerpts=approximate_excerpts,
                    poor_reference_threshold=poor_reference_threshold,
                    duplicate_question_threshold=duplicate_question_threshold,
                )
                queries_generated = True
                # Count number of queries generated
                try:
                    with open(final_queries_path, "r") as f:
                        num_queries_generated = sum(1 for _ in f) - 1  # Exclude header
                except Exception:
                    num_queries_generated = queries_per_corpus * num_rounds

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

        for config in chunking_configs:
            try:
                chunker = create_chunker_from_config(config)
                metrics = evaluation.run(chunker, embedding_function=embedding_func)
                chunker_name = f"{config.provider} {config.chunker_type}"
                chunker_names.append(chunker_name)
                results.append(ChunkingResult(**metrics, chunker_config=config))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error evaluating chunker {config.provider} {config.chunker_type}: {str(e)}",
                )

        return EvaluateResponse(
            embedding_model="text-embedding-3-large",
            document_path=document_path,
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
