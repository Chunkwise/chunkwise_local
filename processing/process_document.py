"""
Contains the orchestration logic for our AWS Batch ECS service for document processing
Takes an S3 bucket, document key, chunker config, and destination database information
Chunks the document, creates embeddings, and writes to the destination database
"""

import time
from utils import get_chunks, get_mapped_embeddings
from services import get_s3_document_text, add_vectors
from config import document_key, table

start_time = time.perf_counter()


def main():
    print(f"Processing document {document_key} of workflow {table}")

    text = get_s3_document_text()

    chunks = get_chunks(text)

    chunk_embedding_pairs = get_mapped_embeddings(chunks)

    add_vectors(chunk_embedding_pairs)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Code execution took {elapsed_time:.4f} seconds.")


if __name__ == "__main__":
    main()
