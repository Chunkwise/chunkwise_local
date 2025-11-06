# Adapted from:
# Minhas, Bhavnick AND Nigam, Shreyash (2025)
# "Chonkie: A no-nonsense fast, lightweight, and efficient text chunking library"
# https://github.com/chonkie-inc/chonkie/blob/65874b1e69b5e8c2cd9a6233818efaf6b948c131/src/chonkie/types/recursive.py#L115
from typing import Literal, Callable, Annotated
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_serializer
from typing import Literal
from chonkie.types import RecursiveRules


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
    LangChainRecursiveConfig
    | LangChainTokenConfig
    | ChonkieRecursiveConfig
    | ChonkieTokenConfig,
    Field(discriminator="chunker_type"),
]
