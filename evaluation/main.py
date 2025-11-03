from dotenv import load_dotenv
import os
from fastapi import FastAPI, Body, HTTPException, UploadFile, File
from typing import List, Literal, Optional, Union, Callable, Any
from pydantic import BaseModel, Field, ConfigDict
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
import chromadb.utils.embedding_functions as embedding_functions
from chonkie.chunker.token import TokenChunker
from chonkie.chunker.recursive import RecursiveChunker
from chonkie.types import RecursiveRules
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter

load_dotenv()

app = FastAPI()

# Create an embedding function (using OpenAI as an example)
API_KEY = os.getenv("OPENAI_API_KEY")
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY, model_name="text-embedding-3-large"
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
    add_start_index: Optional[bool] = False
    strip_whitespace: Optional[bool] = True


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
    document_id: str
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


@app.post("/manual_evaluate")
async def evaluate_chunking(
    # document: UploadFile = File(),
    # questions: UploadFile = File(),
    configs: List[Union[RecursiveChunkerConfig, TokenChunkerConfig]] = Body(
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

    try:
        # Initialize BaseEvaluation
        evaluation = BaseEvaluation(
            questions_csv_path="data/sample_queries.csv",
            corpora_id_paths={"data/sample_document.txt": "data/sample_document.txt"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error initializing BaseEvaluation: {str(e)}"
        )

    results = []
    chunker_names = []

    for config in configs:
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
        document_id="sample_document.txt",
        chunkers_evaluated=chunker_names,
        results=results,
    )
