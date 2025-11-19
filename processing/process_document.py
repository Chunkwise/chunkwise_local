"""
Processing Service
Takes an S3 bucket, document key, chunker config, and destination database
Chunks the document, creates embeddings, and writes to the destination database
"""

import os
import json
import boto3
import psycopg2
import tiktoken
from dotenv import load_dotenv
from psycopg2 import OperationalError
from pydantic import TypeAdapter
from openai import OpenAI
from chunkwise_core import ChunkerConfig
from chunkwise_core.utils import create_chunker
import time

start_time = time.perf_counter()
load_dotenv()

bucket = os.getenv("BUCKET_NAME")
document_key = os.getenv("DOCUMENT_KEY")
config = os.getenv("CHUNK_CONFIG")
openai_api_key = os.getenv("OPENAI_API_KEY")
deployment_id = os.getenv("DEPLOYMENT_ID")

host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


def get_db_connection():
    """
    Creates and returns a connection object for the database.
    """
    try:
        db_connection = psycopg2.connect(
            host=host, database=database, user=user, password=password
        )
        db_connection.autocommit = True
        print("Successfully connected to database.")
        return db_connection

    except OperationalError as e:
        print(("Error connecting to the database.", e))
        raise e


def get_batch_embeddings(chunks, model="text-embedding-3-small", max_tokens=280000):
    client = OpenAI(api_key=openai_api_key)
    enc = tiktoken.get_encoding("cl100k_base")

    batches = []
    current = []
    current_tokens = 0

    for chunk in chunks:
        tokens = len(enc.encode(chunk))
        if current_tokens + tokens > max_tokens:
            batches.append(current)
            current = []
            current_tokens = 0
        current.append(chunk)
        current_tokens += tokens

    if current:
        batches.append(current)

    # embed batches
    embeddings = []
    for batch in batches:
        response = client.embeddings.create(model=model, input=batch)
        embeddings.extend([d.embedding for d in response.data])

    return embeddings


def main():
    # 1. Read the document from S3
    if bucket == "local":
        with open(document_key, "r") as f:
            text = f.read()
    else:
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=document_key)
        text = obj["Body"].read().decode("utf-8")

    # 2. Chunk
    chunker_config = TypeAdapter(ChunkerConfig).validate_json(config)
    chunker = create_chunker(chunker_config)
    chunks = (
        chunker.split_text(text)
        if hasattr(chunker, "split_text")
        else [chunk.text for chunk in chunker(text)]
    )

    # 3. Embed
    embeddings = get_batch_embeddings(chunks)

    # 4. Insert into Postgres
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        insert_sql = """
            INSERT INTO chunk
            (deployment_id, document_key, chunk_id, chunk_text, embedding)
            VALUES (%s, %s, %s, %s, %s)
        """

        for index, chunk in enumerate(chunks):
            cursor.execute(
                insert_sql,
                (deployment_id, document_key, index, chunk, embeddings[index]),
            )
    except Exception as e:
        print(("Error creating workflow.", e))
        raise e
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print(f"Code execution took {elapsed_time:.4f} seconds.")


if __name__ == "__main__":
    main()
