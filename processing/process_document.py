"""
Contains the orchestration logic for our AWS Batch ECS service for document processing
Takes an S3 bucket, document keys, chunker config, and destination database information
Chunks the documents, creates embeddings, and writes to the destination database
"""

from utils import get_chunks, get_mapped_embeddings
from services import get_s3_documents, add_vectors
from config import table


def main():
    print(f"Processing documents of workflow {table}")

    documents = get_s3_documents()

    for document in documents:
        print(f"Processing document {document['key']}")

        chunks = get_chunks(document["text"])

        chunk_embedding_pairs = get_mapped_embeddings(chunks)

        add_vectors(chunk_embedding_pairs, document["key"])


if __name__ == "__main__":
    main()
