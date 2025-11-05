from typing import Any
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from chonkie.chunker.token import TokenChunker
from chonkie.chunker.recursive import RecursiveChunker
from ..types.chunker_config import (
    ChunkerConfig,
    LangChainRecursiveConfig,
    LangChainTokenConfig,
    ChonkieTokenConfig,
    ChonkieRecursiveConfig,
)


def create_chunker(
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
