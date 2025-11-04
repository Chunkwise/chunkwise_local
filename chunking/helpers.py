import re
from typing import Any, Tuple
from chonkie import TokenChunker, RecursiveChunker
from langchain_text_splitters import TokenTextSplitter, RecursiveCharacterTextSplitter
from fuzzywuzzy import fuzz, process
from chunkwise_core import Chunk, RecursiveRules, GeneralChunkerConfig


def create_chunker_from_config(config: GeneralChunkerConfig) -> Any:
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


def find_query_despite_whitespace(document: str, query: str) -> Tuple[int, int] | None:
    # Normalize spaces and newlines in the query
    normalized_query = re.sub(r"\s+", " ", query).strip()

    # Create a regex pattern from the normalized query to match any whitespace characters between words
    pattern = r"\s*".join(re.escape(word) for word in normalized_query.split())

    # Compile the regex to ignore case and search for it in the document
    regex = re.compile(pattern, re.IGNORECASE)
    match = regex.search(document)

    if match:
        return match.start(), match.end()
    else:
        return None


def rigorous_document_search(document: str, target: str) -> Tuple[int, int] | None:
    """
    This function performs a rigorous search of a target string within a document.
    It handles issues related to whitespace, changes in grammar, and other minor text alterations.
    The function first checks for an exact match of the target in the document.
    If no exact match is found, it performs a raw search that accounts for variations in whitespace.
    If the raw search also fails, it splits the document into sentences and uses fuzzy matching
    to find the sentence that best matches the target.

    Args:
        document (str): The document in which to search for the target.
        target (str): The string to search for within the document.

    Returns:
        tuple: A tuple containing the start index and end index of the best match.
        If no match is found, returns None.
    """
    if target.endswith("."):
        target = target[:-1]

    if target in document:
        start_index = document.find(target)
        end_index = start_index + len(target)
        return start_index, end_index
    else:
        raw_search = find_query_despite_whitespace(document, target)
        if raw_search is not None:
            return raw_search

    # Split the text into sentences
    sentences = re.split(r"[.!?]\s*|\n", document)

    # Find the sentence that matches the query best
    best_match = process.extractOne(target, sentences, scorer=fuzz.token_sort_ratio)

    if best_match is None or best_match[1] < 98:
        return None

    reference = best_match[0]

    start_index = document.find(reference)
    end_index = start_index + len(reference)

    return start_index, end_index


def get_chunks(text: str, chunker: GeneralChunkerConfig) -> list[Chunk]:
    """
    Receives text as a string and a chunker
    Adds metadata to chunks if it is a LangChain chunker
    Returns list of chunks
    """
    chunks: list[Chunk] = []

    # LangChain chunkers are called with `split_text`
    # They do not include metadata, so more work is required
    if hasattr(chunker, "split_text"):
        chunks_without_metadata = chunker.split_text(text)
        for chunk in chunks_without_metadata:
            result = rigorous_document_search(text, chunk)

            if result is None:
                print(f"Warning: Could not find chunk in text:\n{chunk[:80]}...")

            else:
                start_index, end_index = result
                chunks.append(
                    Chunk(
                        text=chunk,
                        start_index=start_index,
                        end_index=end_index,
                        token_count=None,
                    )
                )
    # Chonkie chunkers include metadata with chunks
    else:
        chunks = chunker(text)

    return chunks
