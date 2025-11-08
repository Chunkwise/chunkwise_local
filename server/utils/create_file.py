"""
Creates a file based on some passed in text.
"""

import os
from utils import normalize_document


def create_file(file_contents: str):
    """
    Creates a txt file with the provided contents then returns the document id.
    """
    # Create random name
    normalized_document = normalize_document(file_contents)
    document_name = f"{os.urandom(4).hex()}"
    document_id = f"{document_name}.txt"

    # Make sure that the directory exists
    os.makedirs("documents", exist_ok=True)
    # Track temporary file (created from the input `document` string) for cleanup
    temp_doc_path = os.path.join("documents", document_id)

    with open(temp_doc_path, "w", encoding="utf-8") as f:
        f.write(normalized_document)

    return document_id
