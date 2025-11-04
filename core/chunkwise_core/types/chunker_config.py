# Adapted from:
# Minhas, Bhavnick AND Nigam, Shreyash (2025)
# "Chonkie: A no-nonsense fast, lightweight, and efficient text chunking library"
# https://github.com/chonkie-inc/chonkie/blob/65874b1e69b5e8c2cd9a6233818efaf6b948c131/src/chonkie/types/recursive.py#L115
from typing import List, Literal, Optional, Union, Callable, Any
from pydantic import BaseModel, Field, ConfigDict


class RecursiveLevel:
    """RecursiveLevels express the chunking rules at a specific level for the recursive chunker.

    Attributes:
        whitespace (bool): Whether to use whitespace as a delimiter.
        delimiters (Optional[Union[str, List[str]]]): Custom delimiters for chunking.
        include_delim (Optional[Literal["prev", "next"]]): Whether to include the delimiter at all, or in the previous chunk, or the next chunk.
        pattern (Optional[str]): Regex pattern for advanced splitting/extraction.
        pattern_mode (Literal["split", "extract"]): Whether to split on pattern matches or extract pattern matches.

    """

    delimiters: Optional[Union[str, List[str]]] = None
    whitespace: bool = False
    include_delim: Optional[Literal["prev", "next"]] = "prev"
    pattern: Optional[str] = None
    pattern_mode: Literal["split", "extract"] = "split"


class RecursiveRules:
    levels: Optional[List[RecursiveLevel]] = None


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


GeneralChunkerConfig = Union[RecursiveChunkerConfig, TokenChunkerConfig]
