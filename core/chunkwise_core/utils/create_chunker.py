from typing import Any
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    CharacterTextSplitter,
)
from chonkie.chunker import (
    TokenChunker,
    RecursiveChunker,
    SentenceChunker,
    SemanticChunker,
    SlumberChunker,
)
from ..types.chunker_config import (
    ChunkerConfig,
    LangChainCharacterConfig,
    LangChainRecursiveConfig,
    LangChainTokenConfig,
    ChonkieTokenConfig,
    ChonkieRecursiveConfig,
    ChonkieSentenceConfig,
    ChonkieSemanticConfig,
    ChonkieSlumberConfig,
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
        case LangChainCharacterConfig():
            return CharacterTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                separator=config.separator,
                is_separator_regex=config.is_separator_regex,
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
        case ChonkieSentenceConfig():
            return SentenceChunker(
                tokenizer=config.tokenizer,
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                min_sentences_per_chunk=config.min_sentences_per_chunk,
                min_characters_per_sentence=config.min_characters_per_sentence,
                approximate=config.approximate,
                delim=config.delim,
                include_delim=config.include_delim,
            )
        case ChonkieSemanticConfig():
            return SemanticChunker(
                embedding_model=config.embedding_model,
                threshold=config.threshold,
                chunk_size=config.chunk_size,
                similarity_window=config.similarity_window,
                min_sentences_per_chunk=config.min_sentences_per_chunk,
                min_characters_per_sentence=config.min_characters_per_sentence,
            )
        case ChonkieSlumberConfig():
            return SlumberChunker(
                genie=config.genie,
                tokenizer=config.tokenizer,
                chunk_size=config.chunk_size,
                rules=config.rules,
                candidate_size=config.candidate_size,
                min_characters_per_chunk=config.min_characters_per_chunk,
                verbose=config.verbose,
            )
        case _:
            raise ValueError(f"Invalid chunker configuration: {type(config)}")
