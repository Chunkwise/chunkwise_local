import pytest
from types import SimpleNamespace

from fastapi import HTTPException

from server.utils.calculate_chunk_stats import calculate_chunk_stats


def make_chunk(text):
    return SimpleNamespace(text=text)


def test_calculate_chunk_stats_basic():
    chunks = [make_chunk("a"), make_chunk("bb"), make_chunk("ccc")]
    stats = calculate_chunk_stats(chunks)

    assert stats["total_chunks"] == 3
    assert stats["largest_chunk_chars"] == 3
    assert stats["largest_text"] == "ccc"
    assert stats["smallest_chunk_chars"] == 1
    assert stats["smallest_text"] == "a"
    assert stats["avg_chars"] == pytest.approx((1 + 2 + 3) / 3)


def test_calculate_chunk_stats_empty_list():
    stats = calculate_chunk_stats([])

    assert stats["total_chunks"] == 0
    assert stats["avg_chars"] == 0
    # When there are no chunks, largest/smallest keys should not be present
    assert "largest_chunk_chars" not in stats
    assert "smallest_chunk_chars" not in stats


@pytest.mark.parametrize("bad_input", ["not a list", 123, None])
def test_calculate_chunk_stats_invalid_not_list(bad_input):
    with pytest.raises(HTTPException) as exc:
        calculate_chunk_stats(bad_input)  # type: ignore

    assert exc.value.status_code == 400


def test_calculate_chunk_stats_empty_text():
    with pytest.raises(HTTPException) as exc:
        calculate_chunk_stats([make_chunk("")])

    assert exc.value.status_code == 400


def test_calculate_chunk_stats_dict():
    with pytest.raises(HTTPException) as exc:
        calculate_chunk_stats({})

    assert exc.value.status_code == 400


def test_calculate_chunk_stats_int():
    with pytest.raises(HTTPException) as exc:
        calculate_chunk_stats(1)

    assert exc.value.status_code == 400


def test_calculate_chunk_stats_string():
    with pytest.raises(HTTPException) as exc:
        calculate_chunk_stats("string")

    assert exc.value.status_code == 400


def test_calculate_chunk_stats_none():
    with pytest.raises(HTTPException) as exc:
        calculate_chunk_stats(None)

    assert exc.value.status_code == 400
