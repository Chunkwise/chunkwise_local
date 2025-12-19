"""
Configuration file for Chunkwise CDK deployment
"""

from aws_cdk import RemovalPolicy

# Environment Configuration
# Set to "production" for data retention, "development" for auto-cleanup
ENVIRONMENT = "production"  # Options: "production" | "development"

# Docker Image URIs (hardcoded pre-built images)
DOCKER_IMAGES = {
    "server": "public.ecr.aws/x7l1y0z0/chunkwise-server:latest",
    "chunking": "public.ecr.aws/x7l1y0z0/chunkwise-chunking:latest",
    "evaluation": "public.ecr.aws/x7l1y0z0/chunkwise-evaluation:latest",
    "processing": "public.ecr.aws/x7l1y0z0/chunkwise-processing:latest",
}

# VPC Configuration
VPC_CONFIG = {
    "cidr": "10.0.0.0/16",
    "max_azs": 2,
    "nat_gateways": 1,  # One to save cost
}


# ECS Configuration
ECS_CONFIG = {
    "server": {
        "cpu": 512,
        "memory_limit_mib": 1024,
        "desired_count": 1,
        "container_port": 80,
    },
    "chunking": {
        "cpu": 512,
        "memory_limit_mib": 1024,
        "desired_count": 1,
        "container_port": 80,
    },
    "evaluation": {
        "cpu": 512,
        "memory_limit_mib": 1024,
        "desired_count": 1,
        "container_port": 80,
    },
}

# RDS Configuration (Evaluation Database)
RDS_CONFIG = {
    "instance_type": "t4g.micro",
    "database_name": "chunkwise",
    "port": 5432,
    "allocated_storage": 20,  # GB
    "max_allocated_storage": 100,  # GB - for autoscaling
    "backup_retention_days": 0,  # Free tier option
    "multi_az": False,  # Set to True for production HA
    "deletion_protection": ENVIRONMENT == "production",  # Auto-set based on environment
    "publicly_accessible": False,  # Keep evaluation DB private
}

# Vector RDS Configuration (Deployment Database)
VECTOR_RDS_CONFIG = {
    "instance_type": "t4g.micro",  # Same as evaluation DB
    "database_name": "chunkwise_production",
    "port": 5432,
    "allocated_storage": 100,  # GB - larger initial size
    "max_allocated_storage": 500,  # GB - room to grow
    "backup_retention_days": 0,  # Free tier option
    "multi_az": False,  # Set to True for production HA
    "deletion_protection": ENVIRONMENT == "production",  # Auto-set based on environment
    "publicly_accessible": True,  # Allow users to export embeddings
    "allowed_cidrs": [],  # Empty = allow from anywhere. Add specific CIDRs to restrict access
}

# AWS Batch Configuration
BATCH_CONFIG = {
    "max_vcpus": 4,  # Maximum vCPUs for compute environment
    "job_cpu": 1,  # 1 vCPU per job
    "job_memory": 8192,  # 8 GB per job
    "assign_public_ip": True,  # Using public IP to save NAT Gateway costs
}

# S3 Configuration
S3_CONFIG = {"bucket_name_prefix": "chunkwise"}

# Cloud Map Configuration
CLOUD_MAP_CONFIG = {
    "namespace_name": "chunkwise",
    "services": {"chunking": "chunking", "evaluation": "evaluation"},
}

# Environment Variables
# These are set dynamically by the stacks and injected into ECS task definitions
# Listed for documentation purposes only
"""
ENVIRONMENT_VARIABLES = {
    # Evaluation Database (set by DatabaseStack)
    "DB_HOST": evaluation_db.instance_endpoint.hostname
    "DB_NAME": "chunkwise"
    "DB_PORT": "5432"
    "DB_USER": from Secrets Manager
    "DB_PASSWORD": from Secrets Manager

    # Production Vector Database (set by DatabaseStack)
    "VECTOR_DB_HOST": production_db.instance_endpoint.hostname
    "VECTOR_DB_NAME": "chunkwise_production"
    "VECTOR_DB_PORT": "5432"

    # S3 Bucket (set by EcsStack)
    "S3_BUCKET_NAME": documents_bucket.bucket_name

    # Service Discovery (set by EcsStack)
    "CHUNKING_SERVICE_HOST": "chunking.chunkwise"
    "CHUNKING_SERVICE_PORT": "80"
    "EVALUATION_SERVICE_HOST": "evaluation.chunkwise"
    "EVALUATION_SERVICE_PORT": "80"

    # Embedding Configuration
    "EMBEDDING_DIM": "1536"
    
    # Secrets from Secrets Manager
    "OPENAI_API_KEY": from chunkwise/openai-api-key

    # AWS Batch max number of jobs
    "MAX_BATCH_JOBS": BATCH_CONFIG["max_vcpus"] / BATCH_CONFIG["job_cpu"]
}
"""

# Helper Functions
def is_production() -> bool:
    """Check if running in production mode"""
    return ENVIRONMENT == "production"


def get_removal_policy():
    """Get CDK removal policy based on environment"""
    return RemovalPolicy.RETAIN if is_production() else RemovalPolicy.DESTROY
