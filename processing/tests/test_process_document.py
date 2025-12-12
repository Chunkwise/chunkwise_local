from unittest.mock import MagicMock
import pytest
from process_document import main
from chunkwise_core import Chunk

def test_process_document_main(mocker):
    # Mock all the imported functions
    mock_get_text = mocker.patch("process_document.get_s3_document_text", return_value="Document text")

    mock_chunks = [Chunk(text="chunk1"), Chunk(text="chunk2")]
    mock_get_chunks = mocker.patch("process_document.get_chunks", return_value=mock_chunks)

    mock_pairs = [(Chunk(text="chunk1"), [0.1, 0.2]), (Chunk(text="chunk2"), [0.3, 0.4])]
    mock_get_mapped = mocker.patch("process_document.get_mapped_embeddings", return_value=mock_pairs)

    mock_add_vectors = mocker.patch("process_document.add_vectors")

    # Run main
    main()

    mock_get_text.assert_called_once()
    mock_get_chunks.assert_called_once_with("Document text")
    mock_get_mapped.assert_called_once_with(mock_chunks)
    mock_add_vectors.assert_called_once_with(mock_pairs)
