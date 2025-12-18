"""
Services for the processing service
get_db_connection, add_vectors, get_s3_documents
"""

import json
import boto3
import psycopg2
from psycopg2 import OperationalError
from config import host, database, user, password, table, manifest_key, bucket
from chunkwise_core import normalize_document


def get_db_connection() -> None:
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


def add_vectors(chunk_embedding_pairs, document_key: str) -> None:
    """
    Add chunks, embedding vectors, and data into PostgreSQL vector database
    """
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                insert_sql = f"""
                    INSERT INTO {table}
                    (document_key, chunk_index, chunk_text, embedding)
                    VALUES (%s, %s, %s, %s)
                """

                for index, (chunk, embedding) in enumerate(chunk_embedding_pairs):
                    cursor.execute(
                        insert_sql,
                        (document_key, index, chunk, embedding),
                    )
        print("Database connection closed.")
    except Exception as e:
        print(("Error creating workflow.", e))
        raise e


def get_s3_documents():
    """
    Reads documents from a S3 bucket
    Returns a list of dicts containing the S3 document key and normalized text
    """
    s3 = boto3.client("s3")

    # Download the manifest file and get document keys
    response = s3.get_object(Bucket=bucket, Key=manifest_key)
    file_content = response["Body"].read().decode("utf-8")
    doc_keys = json.loads(file_content)

    documents = []
    for key in doc_keys:
        obj = s3.get_object(Bucket=bucket, Key=key)
        text = obj["Body"].read().decode("utf-8")
        normalized_text = normalize_document(text)
        documents.append(
            {
                "key": key,
                "text": normalized_text,
            }
        )
    return documents
