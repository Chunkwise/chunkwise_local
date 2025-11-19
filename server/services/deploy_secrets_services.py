import boto3
import json
import secrets
from botocore.exceptions import ClientError

sm = boto3.client("secretsmanager")

def get_secret(secret_name: str):
    try:
        resp = sm.get_secret_value(SecretId=secret_name)
        if 'SecretString' in resp:
            return json.loads(resp['SecretString']), resp.get('ARN')
        else:
            return None, resp.get('ARN')
    except ClientError as e:
        if e.response['Error']['Code'] in ('ResourceNotFoundException',):
            return None, None
        raise

def create_secret(secret_name: str, username: str):
    password = secrets.token_urlsafe(24)
    secret_value = {"username": username, "password": password}
    resp = sm.create_secret(
        Name=secret_name,
        Description="RDS master credentials for shared workflows DB",
        SecretString=json.dumps(secret_value)
    )
    return secret_value, resp['ARN']

def ensure_secret(secret_name: str, username: str):
    sec, arn = get_secret(secret_name)
    if sec and arn:
        return sec, arn

    # create secret if it does not exist
    sec_val, created_arn = create_secret(secret_name, username=username)
    return sec_val, created_arn
