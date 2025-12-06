"""Configs for the processing service"""

import os
from dotenv import load_dotenv

load_dotenv()

bucket = os.getenv("BUCKET_NAME")
manifest_key = os.getenv("BATCH_MANIFEST_KEY")
chunker_config_json = os.getenv("CHUNKER_CONFIG_JSON")
openai_api_key = os.getenv("OPENAI_API_KEY")

host = os.getenv("VECTOR_DB_HOST")
database = os.getenv("VECTOR_DB_NAME")
table = os.getenv("VECTOR_DB_TABLE")
user = os.getenv("VECTOR_DB_USER")
password = os.getenv("VECTOR_DB_PASSWORD")
