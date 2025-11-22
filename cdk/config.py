"""
Configuration file for Chunkwise CDK deployment
Update these values according to your environment
"""

# Docker Image URIs (hardcoded pre-built images)
# Replace these with your actual ECR image URIs
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
    "database_name": "chunkwise_evaluation",
    "port": 5432,
    "allocated_storage": 20,  # GB
    "max_allocated_storage": 100,  # GB - for autoscaling
    "backup_retention_days": 0,
    "multi_az": False,  # Set to True for production
    "deletion_protection": False,  # Set to True for production
    "publicly_accessible": False,  # Keep evaluation DB private
}

# Vector RDS Configuration (Deployment Database)
VECTOR_RDS_CONFIG = {
    "instance_type": "t4g.micro",  # Same as evaluation DB
    "database_name": "chunkwise_production",
    "port": 5432,
    "allocated_storage": 100,  # GB - larger initial size
    "max_allocated_storage": 500,  # GB - room to grow
    "backup_retention_days": 0,
    "multi_az": False,  # Set to True for production HA
    "deletion_protection": False,  # Set to True for production
    "publicly_accessible": True,  # Allow users to export embeddings
    "allowed_cidrs": [],
}

# AWS Batch Configuration
BATCH_CONFIG = {
    "max_vcpus": 32,  # Maximum vCPUs for compute environment
    "job_cpu": 1,  # 1 vCPU per job
    "job_memory": 2048,  # 2 GB per job
    "assign_public_ip": True,  # Use public IP to save NAT Gateway costs
}

# S3 Configuration
S3_CONFIG = {"bucket_name_prefix": "chunkwise"}  # Will append account ID

# Environment Variables
# WARNING: These will be stored as plaintext in ECS task definitions
ENVIRONMENT_VARIABLES = {
    # Database credentials (will be set from RDS stack)
    # "DB_HOST": "",  # Set dynamically
    # "DB_NAME": "chunkwise",
    # "DB_USER": "postgres",
    # "DB_PASSWORD": "",  # Set dynamically
    # API Keys - UPDATE THESE WITH YOUR ACTUAL KEYS
    # OPENAI_API_KEY": is loaded from AWS Secrets Manager: chunkwise/openai-api-key
    # S3 Bucket - will be set dynamically
    # "S3_BUCKET_NAME": "",
    # Service Discovery - will be set dynamically
    # "CHUNKING_SERVICE_HOST": "chunking.chunkwise",
    # "CHUNKING_SERVICE_PORT": "80",
    # "EVALUATION_SERVICE_HOST": "evaluation.chunkwise",
    # "EVALUATION_SERVICE_PORT": "80"
}

# Cloud Map Configuration
CLOUD_MAP_CONFIG = {
    "namespace_name": "chunkwise",
    "services": {"chunking": "chunking", "evaluation": "evaluation"},
}
