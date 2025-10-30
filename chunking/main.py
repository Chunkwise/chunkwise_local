from fastapi import FastAPI
from chonkie import TokenChunker, RecursiveChunker, RecursiveRules
from langchain_text_splitters import TokenTextSplitter, RecursiveCharacterTextSplitter
from pydantic import BaseModel

app = FastAPI()

# class LangChainChunk(BaseModel):  # LangChain chunks are just strings

class ChonkieChunk(BaseModel):
    text: str           # The chunk text
    start_index: int    # Starting position in original text
    end_index: int      # Ending position in original text
    token_count: int    # Number of tokens in Chunk


class LangChainItem(BaseModel):
    text: str                     # Text to be chunked
    chunk_size: int = 2048        # Maximum tokens per chunk
    chunk_overlap: int = 128      # Overlap between chunks


class ChonkieTokenItem(BaseModel):
    text: str                     # Text to be chunked
    tokenizer: str = "character"  # Default tokenizer (or use "gpt2", etc.)
    chunk_size: int = 2048        # Maximum tokens per chunk
    chunk_overlap: int = 128      # Overlap between chunks


class ChonkieRecursiveItem(BaseModel):
    text: str                                 # Text to be chunked
    tokenizer: str = "character"              # Default tokenizer
    chunk_size: int = 2048                    # Maximum tokens per chunk
    rules: RecursiveRules = RecursiveRules()  # Rules to use for chunking
    min_characters_per_chunk: int = 128       # Smallest chunk size


@app.post("/chunks/token/chonkie")
def chunk(item: ChonkieTokenItem) -> list[ChonkieChunk]:
    chunker = TokenChunker(
      tokenizer=item.tokenizer, 
      chunk_size=item.chunk_size, 
      chunk_overlap=item.chunk_overlap
    )
    chunks = chunker(item.text)
    return chunks


@app.post("/chunks/recursive/chonkie")
def chunk(item: ChonkieRecursiveItem) -> list[ChonkieChunk]:
    chunker = RecursiveChunker(
      tokenizer=item.tokenizer,
      chunk_size=item.chunk_size,
      rules=item.rules,
      min_characters_per_chunk=item.min_characters_per_chunk
    )
    chunks = chunker(item.text)
    return chunks


@app.post("/chunks/token/langchain")
def chunk(item: LangChainItem) -> list[str]:
    chunker = TokenTextSplitter(
      chunk_size=item.chunk_size, 
      chunk_overlap=item.chunk_overlap
    )
    chunks = chunker.split_text(item.text)
    return chunks


@app.post("/chunks/recursive/langchain")
def chunk(item: LangChainItem) -> list[str]:
    chunker = RecursiveCharacterTextSplitter(
      chunk_size=item.chunk_size,
      chunk_overlap=item.chunk_overlap
    )
    chunks = chunker.split_text(item.text)
    return chunks