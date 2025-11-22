import os


# Evaluation Database Configuration (for experimentation workflows)
# These are set by ECS task definition from CDK
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "chunkwise")
DB_SECRET_NAME = "chunkwise/db-credentials"

# Production Vector Database Configuration (for deployment workflows)
# These are set by ECS task definition from CDK
VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST")
VECTOR_DB_PORT = os.getenv("VECTOR_DB_PORT", "5432")
VECTOR_DB_NAME = os.getenv("VECTOR_DB_NAME", "chunkwise_production")
VECTOR_DB_SECRET_NAME = "chunkwise/production-db-credentials"

# Service Discovery Configuration (Cloud Map)
CHUNKING_SERVICE_HOST = os.getenv("CHUNKING_SERVICE_HOST", "localhost")
CHUNKING_SERVICE_PORT = int(os.getenv("CHUNKING_SERVICE_PORT", "1111"))
EVALUATION_SERVICE_HOST = os.getenv("EVALUATION_SERVICE_HOST", "localhost")
EVALUATION_SERVICE_PORT = int(os.getenv("EVALUATION_SERVICE_PORT", "2222"))

# S3 Configuration
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Embedding Configuration
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))
