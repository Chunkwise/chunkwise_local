from fastapi import FastAPI
from chonkie import TokenChunker
from pydantic import BaseModel

app = FastAPI()
chunker = TokenChunker(
tokenizer="character", # Default tokenizer (or use "gpt2", etc.)
chunk_size=10, # Maximum tokens per chunk
chunk_overlap=0 # Overlap between chunks
)

class Item(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"Hello World"}

@app.post("/chunks")
def chunk(item: Item):
    chunks = chunker(item.text)
    return chunks