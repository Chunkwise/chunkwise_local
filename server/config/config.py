import os

DBNAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
ENDPOINT = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")

vec_db_host = os.getenv("VEC_DB_HOST")
vec_db_port = os.getenv("VEC_DB_PORT")
vec_db_name = os.getenv("VEC_DB_NAME")
vec_db_user = os.getenv("VEC_DB_USER")
vec_db_password = os.getenv("VEC_DB_PASSWORD")

CHUNKING_SERVICE_HOST = os.getenv("CHUNKING_SERVICE_HOST", "localhost")
CHUNKING_SERVICE_PORT = int(os.getenv("CHUNKING_SERVICE_PORT", "1111"))
EVALUATION_SERVICE_HOST = os.getenv("EVALUATION_SERVICE_HOST", "localhost")
EVALUATION_SERVICE_PORT = int(os.getenv("EVALUATION_SERVICE_PORT", "2222"))

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))
