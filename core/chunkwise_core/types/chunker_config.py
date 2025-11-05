# Adapted from:
# Minhas, Bhavnick AND Nigam, Shreyash (2025)
# "Chonkie: A no-nonsense fast, lightweight, and efficient text chunking library"
# https://github.com/chonkie-inc/chonkie/blob/65874b1e69b5e8c2cd9a6233818efaf6b948c131/src/chonkie/types/recursive.py#L115
import re
from typing import Literal, Callable, Annotated
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_serializer
from typing import Iterator, Literal


@dataclass
class RecursiveLevel:
    """RecursiveLevels express the chunking rules at a specific level for the recursive chunker.

    Attributes:
        whitespace (bool): Whether to use whitespace as a delimiter.
        delimiters (Optional[Union[str, List[str]]]): Custom delimiters for chunking.
        include_delim (Optional[Literal["prev", "next"]]): Whether to include the delimiter at all, or in the previous chunk, or the next chunk.
        pattern (Optional[str]): Regex pattern for advanced splitting/extraction.
        pattern_mode (Literal["split", "extract"]): Whether to split on pattern matches or extract pattern matches.

    """

    delimiters: str | list[str] | None = None
    whitespace: bool = False
    include_delim: Literal["prev", "next"] | None = "prev"
    pattern: str | None = None
    pattern_mode: Literal["split", "extract"] = "split"

    def _validate_fields(self) -> None:
        """Validate all fields have legal values."""
        # Check for mutually exclusive options
        active_options = sum(
            [bool(self.delimiters), self.whitespace, bool(self.pattern)]
        )

        if active_options > 1:
            raise NotImplementedError(
                "Cannot use multiple splitting methods simultaneously. Choose one of: delimiters, whitespace, or pattern."
            )

        if self.delimiters is not None:
            if isinstance(self.delimiters, str) and len(self.delimiters) == 0:
                raise ValueError("Custom delimiters cannot be an empty string.")
            if isinstance(self.delimiters, list):
                if any(
                    not isinstance(delim, str) or len(delim) == 0
                    for delim in self.delimiters
                ):
                    raise ValueError("Custom delimiters cannot be an empty string.")
                if any(delim == " " for delim in self.delimiters):
                    raise ValueError(
                        "Custom delimiters cannot be whitespace only. Set whitespace to True instead."
                    )

        if self.pattern is not None:
            if not isinstance(self.pattern, str) or len(self.pattern) == 0:
                raise ValueError("Pattern must be a non-empty string.")
            try:
                re.compile(self.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")

        if self.pattern_mode not in ["split", "extract"]:
            raise ValueError("pattern_mode must be either 'split' or 'extract'.")

    def __post_init__(self) -> None:
        """Validate attributes."""
        self._validate_fields()

    def __repr__(self) -> str:
        """Return a string representation of the RecursiveLevel."""
        return (
            f"RecursiveLevel(delimiters={self.delimiters}, "
            f"whitespace={self.whitespace}, include_delim={self.include_delim}, "
            f"pattern={self.pattern}, pattern_mode={self.pattern_mode})"
        )

    def to_dict(self) -> dict:
        """Return the RecursiveLevel as a dictionary."""
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict) -> "RecursiveLevel":
        """Create RecursiveLevel object from a dictionary."""
        return cls(**data)


@dataclass
class RecursiveRules:
    """Expression rules for recursive chunking."""

    levels: list[RecursiveLevel] | None = None

    def __post_init__(self) -> None:
        """Validate attributes."""
        if self.levels is None:
            paragraphs = RecursiveLevel(delimiters=["\n\n", "\r\n", "\n", "\r"])
            sentences = RecursiveLevel(
                delimiters=[". ", "! ", "? "],
            )
            pauses = RecursiveLevel(
                delimiters=[
                    "{",
                    "}",
                    '"',
                    "[",
                    "]",
                    "<",
                    ">",
                    "(",
                    ")",
                    ":",
                    ";",
                    ",",
                    "—",
                    "|",
                    "~",
                    "-",
                    "...",
                    "`",
                    "'",
                ],
            )
            word = RecursiveLevel(whitespace=True)
            token = RecursiveLevel()
            self.levels = [paragraphs, sentences, pauses, word, token]
        elif isinstance(self.levels, list):
            for level in self.levels:
                level._validate_fields()
        else:
            raise ValueError("Levels must be a list of RecursiveLevel objects.")

    def __repr__(self) -> str:
        """Return a string representation of the RecursiveRules."""
        return f"RecursiveRules(levels={self.levels})"

    def __len__(self) -> int:
        """Return the number of levels."""
        return len(self.levels) if self.levels is not None else 0

    def __getitem__(self, index: int) -> RecursiveLevel | None:
        """Return the RecursiveLevel at the specified index."""
        return self.levels[index] if self.levels is not None else None

    def __iter__(self) -> Iterator[RecursiveLevel] | None:
        """Return an iterator over the RecursiveLevels."""
        return iter(self.levels) if self.levels is not None else None

    @classmethod
    def from_dict(cls, data: dict) -> "RecursiveRules":
        """Create a RecursiveRules object from a dictionary."""
        dict_levels = data.get("levels", None)
        object_levels: list[RecursiveLevel] | None = None
        if dict_levels is not None:
            if isinstance(dict_levels, dict):
                object_levels = [RecursiveLevel.from_dict(dict_levels)]
            elif isinstance(dict_levels, list):
                object_levels = [
                    RecursiveLevel.from_dict(d_level) for d_level in dict_levels
                ]
        return cls(levels=object_levels)

    def to_dict(self) -> dict:
        """Return the RecursiveRules as a dictionary."""
        result: {str, List[Dict] | None} = dict()
        result["levels"] = (
            [level.to_dict() for level in self.levels]
            if self.levels is not None
            else None
        )
        return result


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
