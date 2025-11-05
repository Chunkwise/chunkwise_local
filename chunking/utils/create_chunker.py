from typing import Any
from chonkie import TokenChunker, RecursiveChunker
from langchain_text_splitters import TokenTextSplitter, RecursiveCharacterTextSplitter
from chunkwise_core import GeneralChunkerConfig, RecursiveRules


def create_chunker(config: GeneralChunkerConfig) -> Any:
    """
    Receives a chunker config
    Returns a chunker
    """
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
