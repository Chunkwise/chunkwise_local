"""
Services for the processing service
get_db_connection, add_vectors, get_s3_document_text
"""

import boto3
import psycopg2
from psycopg2 import OperationalError
from config import host, database, user, password, table, document_key, bucket


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


def add_vectors(chunk_embedding_pairs) -> None:
    """
    Add chunks, embedding vectors, and data into PostgreSQL vector database
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

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
    except Exception as e:
        print(("Error creating workflow.", e))
        raise e
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def normalize_document(content: str) -> str:
    """Normalize smart quotes and dashes in the document to standard ASCII characters."""
    content = content.replace("\u2018", "'")  #  → '
    content = content.replace("\u2019", "'")  # ’ → '
    content = content.replace("\u201c", '"')  # ” → "
    content = content.replace("\u201d", '"')  # " → "
    content = content.replace("\u2013", "-")  # – → -
    content = content.replace("\u2014", "-")  # — → -
    return content


def get_s3_document_text(local: bool = False) -> str:
    """
    Local testing: reads a local file and returns normalized text
    AWS deployment: reads a document from a S3 bucket and returns normalized text
    """
    if local:
        with open(document_key, "r") as f:
            text = f.read()
    else:
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=document_key)
        text = obj["Body"].read().decode("utf-8")
    normalized_text = normalize_document(text)
    return normalized_text
