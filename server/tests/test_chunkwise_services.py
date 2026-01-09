import asyncio
from types import SimpleNamespace

import pytest
import requests

from server.services.chunkwise_services import get_chunks, get_evaluation
from server.config.config import (
    CHUNKING_SERVICE_HOST,
    CHUNKING_SERVICE_PORT,
    EVALUATION_SERVICE_HOST,
    EVALUATION_SERVICE_PORT,
)


def test_get_chunks_success(monkeypatch):
    captured = {}

    def mock_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout

        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return [
                    {"text": "chunk1", "id": 1},
                    {"text": "chunk2", "id": 2},
                ]

        return Resp()

    monkeypatch.setattr("server.services.chunkwise_services.requests.post", mock_post)

    chunker_config = SimpleNamespace(model_dump=lambda: {"chunk_size": 100})
    chunks = asyncio.run(get_chunks(chunker_config, "document text"))

    expected_url = (
        f"http://{CHUNKING_SERVICE_HOST}:{CHUNKING_SERVICE_PORT}/chunk_with_metadata"
    )
    assert captured["url"] == expected_url
    assert captured["json"] == {
        "chunker_config": {"chunk_size": 100},
        "text": "document text",
    }
    assert captured["timeout"] == 120

    assert len(chunks) == 2
    assert hasattr(chunks[0], "text") and chunks[0].text == "chunk1"


def test_get_chunks_http_error_propagates(monkeypatch):
    class Resp:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("boom")

        def json(self):
            return []

    monkeypatch.setattr(
        "server.services.chunkwise_services.requests.post", lambda *a, **k: Resp()
    )

    chunker_config = SimpleNamespace(model_dump=lambda: {"chunk_size": 5})
    with pytest.raises(requests.exceptions.HTTPError):
        asyncio.run(get_chunks(chunker_config, "doc"))


def test_get_evaluation_success(monkeypatch):
    captured = {}

    evaluation_json = {
        "embedding_model": "emb",
        "corpus_id": "c",
        "document_s3_key": "d",
        "queries_s3_key": "q",
        "queries_generated": True,
        "num_queries": 1,
        "chunkers_evaluated": ["c1"],
        "results": [
            {
                "iou_mean": 0.1,
                "recall_mean": 0.2,
                "precision_mean": 0.3,
                "precision_omega_mean": 0.4,
            }
        ],
    }

    def mock_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout

        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return evaluation_json

        return Resp()

    monkeypatch.setattr("server.services.chunkwise_services.requests.post", mock_post)

    chunker_config = SimpleNamespace(model_dump=lambda: {"chunk_size": 10})
    out = asyncio.run(get_evaluation(chunker_config, "doc-id"))

    expected_url = (
        f"http://{EVALUATION_SERVICE_HOST}:{EVALUATION_SERVICE_PORT}/evaluate"
    )
    assert captured["url"] == expected_url
    assert captured["json"] == {
        "chunking_configs": [{"chunk_size": 10}],
        "document_id": "doc-id",
    }
    assert captured["timeout"] == 240

    assert out == evaluation_json


def test_get_evaluation_http_error_propagates(monkeypatch):
    class Resp:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("bad eval")

        def json(self):
            return {}

    monkeypatch.setattr(
        "server.services.chunkwise_services.requests.post", lambda *a, **k: Resp()
    )

    chunker_config = SimpleNamespace(model_dump=lambda: {"chunk_size": 5})
    with pytest.raises(requests.exceptions.HTTPError):
        asyncio.run(get_evaluation(chunker_config, "doc-id"))
