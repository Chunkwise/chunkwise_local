import os
from typing import Literal, Callable, Annotated
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_serializer
from chonkie.types import RecursiveRules
from chonkie.genie import OpenAIGenie
from chonkie.embeddings import OpenAIEmbeddings

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ChunkerConfig models using Pydantic v2
# Only considering 4 chunkers for now
class LangChainBaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    provider: Literal["langchain"] = "langchain"
    chunk_size: int = Field(default=4000, ge=1)
    chunk_overlap: int = Field(default=200, ge=0)
    length_function: Callable[[str], int] = len
    keep_separator: bool | Literal["start", "end"] = False
    add_start_index: bool = False
    strip_whitespace: bool = True

    @model_validator(mode="after")
    def validate_overlap(self) -> "LangChainBaseConfig":
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


class LangChainCharacterConfig(LangChainBaseConfig):
    chunker_type: Literal["character"] = "character"
    separator: str = "\n\n"
    is_separator_regex: bool = False


class LangChainRecursiveConfig(LangChainBaseConfig):
    chunker_type: Literal["recursive"] = "recursive"
    separators: list[str] | None = None
    keep_separator: bool | Literal["start", "end"] = True
    is_separator_regex: bool = False


class LangChainTokenConfig(LangChainBaseConfig):
    chunker_type: Literal["token"] = "token"
    encoding_name: str = "gpt2"
    model_name: str | None = None
    allowed_special: Literal["all"] | set[str] = Field(default_factory=set)
    disallowed_special: Literal["all"] | set[str] = "all"


class ChonkieBaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    provider: Literal["chonkie"] = "chonkie"
    tokenizer: Literal["character", "word", "gpt2"] | str = "gpt2"


class ChonkieRecursiveConfig(ChonkieBaseConfig):
    chunker_type: Literal["recursive"] = "recursive"
    tokenizer: Literal["character", "word", "gpt2"] | str = "character"
    rules: RecursiveRules = Field(default_factory=RecursiveRules)
    chunk_size: int = Field(default=2048, gt=0)
    min_characters_per_chunk: int = Field(default=24, gt=0)


class ChonkieTokenConfig(ChonkieBaseConfig):
    chunker_type: Literal["token"] = "token"
    tokenizer: Literal["character", "word", "gpt2"] | str = "character"
    chunk_size: int = Field(default=2048, gt=0)
    chunk_overlap: int | float = Field(default=0, ge=0)

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


class ChonkieSentenceConfig(ChonkieBaseConfig):
    chunker_type: Literal["sentence"] = "sentence"
    tokenizer: Literal["character", "word", "gpt2"] | str = "character"
    chunk_size: int = 2048
    chunk_overlap: int = 0
    min_sentences_per_chunk: int = 1
    min_characters_per_sentence: int = 12
    approximate: bool = False
    delim: str | list[str] = [". ", "! ", "? ", "\n"]
    include_delim: Literal["prev", "next"] | None = "prev"


class ChonkieSemanticConfig(ChonkieBaseConfig):
    chunker_type: Literal["semantic"] = "semantic"
    embedding_model: str | OpenAIEmbeddings | None = None
    threshold: float = 0.8
    chunk_size: int = 2048
    similarity_window: int = 3
    min_sentences_per_chunk: int = 1
    min_characters_per_sentence: int = 24
    delim: str | list[str] = [". ", "! ", "? ", "\n"]
    include_delim: Literal["prev", "next"] | None = "prev"
    skip_window: int = 0
    filter_window: int = 5
    filter_polyorder: int = 3
    filter_tolerance: float = 0.2


class ChonkieSlumberConfig(ChonkieBaseConfig):
    chunker_type: Literal["slumber"] = "slumber"
    genie: OpenAIGenie | None = None
    tokenizer: Literal["character", "word", "gpt2"] | str = "character"
    chunk_size: int = 2048
    rules: RecursiveRules = RecursiveRules()
    candidate_size: int = 128
    min_characters_per_chunk: int = 24
    verbose: bool = True


LangChainConfigs = Annotated[
    LangChainCharacterConfig | LangChainRecursiveConfig | LangChainTokenConfig,
    Field(discriminator="chunker_type"),
]

ChonkieConfigs = Annotated[
    ChonkieRecursiveConfig
    | ChonkieTokenConfig
    | ChonkieSentenceConfig
    | ChonkieSemanticConfig
    | ChonkieSlumberConfig,
    Field(discriminator="chunker_type"),
]

ChunkerConfig = Annotated[
    LangChainConfigs | ChonkieConfigs,
    Field(discriminator="provider"),
]
