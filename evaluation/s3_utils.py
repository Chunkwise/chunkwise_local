"""
S3 utilities for document and query storage.

This module provides functions to interact with AWS S3 for:
- Uploading and downloading documents
- Uploading and downloading query CSV files
- Checking if objects exist in S3
"""

import os
import logging
import tempfile
from contextlib import contextmanager
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

BUCKET_NAME = "chunkwise-test-eval"

_s3_client = None 

def _get_s3_client():
    """
    Get a boto3 S3 client using implicit credentials.
    Reuses the same client across calls for efficiency.

    Credentials are automatically loaded from:
    - AWS CLI config (~/.aws/credentials)
    - Environment variables
    - IAM roles (if running on AWS)

    Returns:
        boto3 S3 client
    """
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
        # Validate bucket exists
        try:
            _s3_client.head_bucket(Bucket=BUCKET_NAME)
        except ClientError:
            logger.error("S3 bucket %s does not exist or is not accessible", BUCKET_NAME)
            raise
    return _s3_client


def upload_file(local_path: str, s3_key: str) -> bool:
    """
    Upload a file to S3.

    Args:
        local_path: Path to local file
        s3_key: S3 object key (path within bucket)

    Returns:
        True if upload successful, False otherwise
    """
    try:
        s3_client = _get_s3_client()
        s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
        logger.info(
            "Successfully uploaded %s to s3://%s/%s", local_path, BUCKET_NAME, s3_key
        )
        return True
    except FileNotFoundError:
        logger.error("Local file not found: %s", local_path)
        return False
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        return False
    except ClientError as e:
        logger.error("Error uploading to S3: %s", e)
        return False


def download_file(s3_key: str, local_path: str) -> bool:
    """
    Download a file from S3 to a specific local path.

    Args:
        s3_key: S3 object key (path within bucket)
        local_path: Path where to save the downloaded file

    Returns:
        True if download successful, False otherwise
    """
    try:
        # Ensure the directory exists
        dir_path = os.path.dirname(local_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        s3_client = _get_s3_client()
        s3_client.download_file(BUCKET_NAME, s3_key, local_path)
        logger.info(
            "Successfully downloaded s3://%s/%s to %s", BUCKET_NAME, s3_key, local_path
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error("S3 object not found: s3://%s/%s", BUCKET_NAME, s3_key)
        else:
            logger.error("Error downloading from S3: %s", e)
        return False
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        return False


@contextmanager
def download_file_temp(s3_key: str, suffix: str | None):
    """
    Download a file from S3 to a temporary file (context manager).

    The temporary file is automatically cleaned up when the context exits.
    Works seamlessly in both local development and AWS Lambda.

    Args:
        s3_key: S3 object key (path within bucket)
        suffix: Optional file suffix (e.g., '.txt', '.csv')

    Yields:
        str: Path to the temporary file, or None if download failed
    """
    temp_file = None
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode="w+b", suffix=suffix or "", delete=False
        )
        temp_path = temp_file.name
        temp_file.close()

        # Download from S3
        s3_client = _get_s3_client()
        s3_client.download_file(BUCKET_NAME, s3_key, temp_path)
        logger.info(
            "Successfully downloaded s3://%s/%s to temp file %s",
            BUCKET_NAME,
            s3_key,
            temp_path,
        )

        yield temp_path

    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error("S3 object not found: s3://%s/%s", BUCKET_NAME, s3_key)
        else:
            logger.error("Error downloading from S3: %s", e)
        yield None
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        yield None
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception as e:
                logger.warning(
                    "Failed to delete temporary file %s: %s", temp_file.name, e
                )


def exists(s3_key: str) -> bool:
    """
    Check if an object exists in S3.

    Args:
        s3_key: S3 object key (path within bucket)

    Returns:
        True if object exists, False otherwise
    """
    try:
        s3_client = _get_s3_client()
        s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False

        logger.error("Error checking S3 object existence: %s", e)
        return False
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        return False


def delete_file(s3_key: str) -> bool:
    """
    Delete a file from S3.

    Args:
        s3_key: S3 object key (path within bucket)

    Returns:
        True if deletion successful, False otherwise
    """
    try:
        s3_client = _get_s3_client()
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        logger.info("Successfully deleted s3://%s/%s", BUCKET_NAME, s3_key)
        return True
    except ClientError as e:
        logger.error("Error deleting from S3: %s", e)
        return False
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        return False


def list_files(prefix: str = "") -> list[str]:
    """
    List files in the S3 bucket with optional prefix filter.

    Args:
        prefix: Optional prefix to filter objects (e.g., "documents/")

    Returns:
        List of S3 keys (file names)
    """
    try:
        s3_client = _get_s3_client()
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        if "Contents" not in response:
            return []

        return [obj["Key"] for obj in response["Contents"]]
    except ClientError as e:
        logger.error("Error listing S3 objects: %s", {e})
        return []
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        return []


def get_document_s3_key(document_id: str) -> str:
    """
    Get S3 key for a document.

    Note: Document normalization is handled by upstream orchestration server,
    so it's assumed that all documents in S3 are already normalized.

    Args:
        document_id: Document identifier (with or without .txt extension)

    Returns:
        S3 key in format: documents/{document_id}.txt
    """
    # Remove .txt extension if present
    if document_id.endswith(".txt"):
        document_id = document_id[:-4]

    return f"documents/{document_id}.txt"


def get_queries_s3_key(document_id: str) -> str:
    """
    Get S3 key for queries CSV.

    Args:
        document_id: Document identifier (with or without .txt extension)

    Returns:
        S3 key in format: queries/{document_id}/llm_queries_{document_id}.csv
    """
    # Remove .txt extension if present
    if document_id.endswith(".txt"):
        document_id = document_id[:-4]

    return f"queries/{document_id}/llm_queries_{document_id}.csv"


def is_s3_configured() -> bool:
    """
    Check if S3 is properly configured.
    
    Returns:
        True if S3 client can be created and credentials are available
    """
    try:
        s3_client = _get_s3_client()
        # Try a simple operation to verify credentials
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        return True
    except (ClientError, NoCredentialsError):
        return False
