import pytest
from utils.calculate_chunk_stats import calculate_chunk_stats
from server_types import Chunk
from fastapi import HTTPException

def test_calculate_chunk_stats_valid():
    chunks = [
        Chunk(text="Hello"),
        Chunk(text="World!")
    ]
    stats = calculate_chunk_stats(chunks)
    assert stats["total_chunks"] == 2
    assert stats["largest_chunk_chars"] == 6 # World!
    assert stats["smallest_chunk_chars"] == 5 # Hello
    assert stats["avg_chars"] == 5.5

def test_calculate_chunk_stats_empty():
    chunks = []
    stats = calculate_chunk_stats(chunks)
    assert stats["total_chunks"] == 0
    assert stats["avg_chars"] == 0

def test_calculate_chunk_stats_invalid_input():
    with pytest.raises(HTTPException):
        calculate_chunk_stats("not a list")

def test_calculate_chunk_stats_missing_text():
    chunks = [Chunk(text="ok"), Chunk(text=None)]
    with pytest.raises(HTTPException):
        calculate_chunk_stats(chunks)
