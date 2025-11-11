"""
This file contains the list of services involving s3. This includes:
uploading a file, downloading a file, deleting a file, and getting the
ids of files in a bucket.
"""

import logging
import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = "chunkwise-sample"


async def upload_s3_file(document_id):
    """Upload a file to s3"""
    try:
        s3_client = boto3.client("s3")
        s3_client.upload_file(
            f"documents/{document_id}.txt", BUCKET_NAME, f"documents/{document_id}.txt"
        )
        return True

    except ClientError:
        logging.exception("s3 ClientError while uploading document")


async def download_s3_file(document_id):
    """Download a file from s3"""
    try:
        s3_client = boto3.client("s3")
        s3_client.download_file(
            BUCKET_NAME, f"documents/{document_id}.txt", f"documents/{document_id}.txt"
        )
        return True

    except ClientError:
        logging.exception("s3 ClientError while downloading document")


async def delete_s3_file(document_id):
    """Delete a file on s3"""
    try:
        s3_client = boto3.client("s3")
        s3_client.delete_object(Key=document_id, Bucket=BUCKET_NAME)
        return True

    except ClientError:
        logging.exception("s3 ClientError while deleting document")


async def get_s3_file_names():
    """Get the list of resources from a bucket"""
    try:
        s3_client = boto3.client("s3")
        resources = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        # Create a list of the files names of a bucket
        file_names = [resource["Key"] for resource in resources["Contents"]]
        return file_names

    except ClientError:
        logging.exception("s3 ClientError while getting document names")
