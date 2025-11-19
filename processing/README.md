# Processing Service

This service processes documents. It takes a document from an S3 bucket, chunks and embeds it, and writes the data to a specified RDS PostgreSQL vector database.

## To install dependencies

`poetry install`

## Local testing

1. Install pgvector (macOS)

`brew install pgvector`

2. Restart postgresql (macOS)

`brew services restart postgresql`

3. Create a postgresql database

4. Create a vector extension and tables (see `vector_schema.sql` in `chunkwise_local` root)

5. Create a .env with the following variables:

BUCKET_NAME=local
DOCUMENT_KEY="../evaluation/data/sample_document_large.txt"
CHUNK_CONFIG={"provider":"langchain","chunk_size":300,"chunk_overlap":0,"chunker_type":"token"}
OPENAI_API_KEY=

DB_HOST=localhost
DB_NAME=
DB_TABLE=workflow_1
DB_USER=
DB_PASSWORD=

6. Run the service

`python3 process_document.py`
