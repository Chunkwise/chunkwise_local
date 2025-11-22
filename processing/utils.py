"""
Utility functions for the processing service
get_chunks, normalize_document, get_mapped_embeddings
"""

import time
import random
import tiktoken
from pydantic import TypeAdapter
from openai import OpenAI, RateLimitError
from chunkwise_core import ChunkerConfig
from chunkwise_core.utils import create_chunker
from config import openai_api_key, chunker_config


def get_chunks(text: str) -> list[str]:
    """
    Takes a text to be chunked
    Creates a chunker based on the chunking config (env variable)
    Cleans chunks because the OpenAI embedding API does not accept empty/whitespace only chunks
    Return chunks as a list of strings
    """
    adapted_chunker_config = TypeAdapter(ChunkerConfig).validate_json(chunker_config)
    chunker = create_chunker(adapted_chunker_config)
    chunks = (
        chunker.split_text(text)
        if hasattr(chunker, "split_text")
        else [chunk.text for chunk in chunker(text)]
    )
    valid_chunks = [c for c in chunks if c and c.strip()]
    return valid_chunks


def retry_with_backoff(func, retries=9, initial_delay=2, backoff_factor=1.5):
    """
    Retries a function if it hits a RateLimitError.
    Waits exponentially longer between retries.
    """

    def wrapper(*args, **kwargs):
        delay = initial_delay
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError:
                if i == retries - 1:
                    print("Max retries reached. Failing.")
                    raise

                # Add jitter to prevent 'thundering herd' since we are running multiple instances
                delay += random.uniform(0, 1)
                print(f"Rate limited. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
                delay *= backoff_factor
            except Exception as e:
                raise e

    return wrapper


def get_mapped_embeddings(
    chunks: list[str], model="text-embedding-3-small", max_tokens=280000
):
    """
    Takes in chunks as a list of strings
    Batches chunks into groups below the 300k token OpenAI API limit
    Filters chunks of size 0 and ensure batches are under 2048 in length (OpenAI limit)
    Returns mapping of chunks to embeddings
    """
    client = OpenAI(api_key=openai_api_key)
    enc = tiktoken.get_encoding("cl100k_base")

    # Wrap the API call with our retry logic
    @retry_with_backoff
    def call_openai_api(batch_input):
        return client.embeddings.create(model=model, input=batch_input)

    batches = []
    current = []
    current_tokens = 0

    for chunk in chunks:
        tokens = len(enc.encode(chunk))
        if tokens == 0:
            print(f"Skipping chunk with 0 tokens: {repr(chunk)}")
            continue

        if tokens > 8191:
            chunk = enc.decode(enc.encode(chunk)[:8191])
            tokens = 8191
            print(f"Chunk too large: {tokens} tokens > 8191. Truncated chunk.")

        if current_tokens + tokens > max_tokens or len(current) >= 2048:
            batches.append(current)
            current = []
            current_tokens = 0
        current.append(chunk)
        current_tokens += tokens

    if current:
        batches.append(current)

    results = []

    print(f"Processing {len(batches)} batches...")

    for i, batch_chunks in enumerate(batches):
        try:
            response = call_openai_api(batch_chunks)
            batch_embeddings = [d.embedding for d in response.data]
            paired_data = list(zip(batch_chunks, batch_embeddings))
            results.extend(paired_data)

        except Exception as e:
            print(f"Failed to embed batch {i}. Skipping these chunks. Error: {e}")
            print(f"Chunk: {batches[i]}")
            raise e

    return results
