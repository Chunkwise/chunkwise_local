"""
This file contains the list of services involving s3. This includes:
uploading a file, downloading a file, deleting a file, and getting the
ids of files in a bucket.
"""

import os
import logging
import boto3
from botocore.exceptions import ClientError
from config import BUCKET_NAME


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
    """Download a file from s3 to local directory /documents"""
    try:
        os.makedirs("documents", exist_ok=True)

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
        result = s3_client.delete_object(
            Key=f"documents/{document_id}.txt", Bucket=BUCKET_NAME
        )
        if result["ResponseMetadata"]["HTTPStatusCode"] == 204:
            return True
        else:
            return False

    except ClientError:
        logging.exception("s3 ClientError while deleting document")


async def get_s3_file_names():
    """Get the list of resources from a bucket"""
    try:
        s3_client = boto3.client("s3")
        resources = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="documents")

        # Create a list of the files names of a bucket, remove the beginning path

        if not "Contents" in resources:
            return []

        file_names = [
            resource["Key"].replace("documents/", "").replace(".txt", "")
            for resource in resources["Contents"]
        ]
        return file_names

    except ClientError:
        logging.exception("s3 ClientError while getting document names")
