
# Chunkwise CDK Deployment

This CDK application automates the deployment of Chunkwise, a document chunking evaluation platform, to AWS.

## Architecture Overview

The deployment creates:
- **VPC**: Custom VPC with public and private subnets across 2 availability zones
- **ECS Fargate**: Three containerized microservices (server, chunking, evaluation)
- **RDS PostgreSQL**: Relational database for chunking visualization and evaluation results
- **Application Load Balancer**: Routes external traffic to the server service
- **AWS Cloud Map**: Service discovery for inter-service communication
- **S3**: Stores documents to evaluate and LLM-generated queries
- **CloudWatch**: Centralized logging for monitoring all services

## Prerequisites

Before deploying, make sure you have:

1. **AWS CLI** configured with appropriate credentials
```bash
   aws configure
```

3. **Python 3.7+** installed

4. **Node.js 22.x+ and npm** installed

5. **AWS CDK** installed globally
```bash
   npm install -g aws-cdk
```

6. **OpenAI API Key** stored in AWS Secrets Manager (see below)

7. **(Optional) Docker** installed and running (the app will use pre-built images stored in a public ECR repository by default; Docker is only required if you want to build your own images, see below)

## Initial Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Chunkwise/chunkwise_local.git
cd chunkwise_local/cdk
```

### 2. Create Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Bootstrap CDK (First Time Only)

If this is your first time using CDK in your AWS account/region:
```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

Example:
```bash
cdk bootstrap aws://123456789012/us-west-2
```

### 5. Store OpenAI API Key in Secrets Manager

**This is the only manual setup required!**
```bash
aws secretsmanager create-secret \
    --name chunkwise/openai-api-key \
    --description "OpenAI API key for Chunkwise chunking and evaluation service" \
    --secret-string "sk-your-openai-api-key-here" \
```

Verify the secret was created:
```bash
aws secretsmanager describe-secret \
    --secret-id chunkwise/openai-api-key \
```

### 6. (Optional) Adjust configurations and resource sizes if needed in `config.py`

If you want to use your own images, update the URIs (from ECR):
```python
DOCKER_IMAGES = {
    "server": "123456789012.dkr.ecr.us-east-1.amazonaws.com/chunkwise-server:latest",
    "chunking": "123456789012.dkr.ecr.us-east-1.amazonaws.com/chunkwise-chunking:latest",
    "evaluation": "123456789012.dkr.ecr.us-east-1.amazonaws.com/chunkwise-evaluation:latest"
}
```

## Deployment

### Option 1: Deploy All Stacks at Once (Recommended)
```bash
cdk deploy --all
```

This will deploy all four stacks:
1. `ChunkwiseNetworkStack` - Creates a custom VPC with public/private subnets across 2 availability zones and networking
2. `ChunkwiseLoadBalancerStack` - Creates an application load balancer with a listener and a target group, and a security group
3. `ChunkwiseDatabaseStack` - Creates an RDS PostgreSQL instance, a subnet group, and a security group
4. `ChunkwiseEcsStack` - Creates an ECS cluster, 3 task definitions and services, a cloud map, an S3 bucket, necessary IAM roles, CloudWatch log groups, and a security group

### Option 2: Deploy Stacks Individually
```bash
cdk deploy ChunkwiseNetworkStack
cdk deploy ChunkwiseLoadBalancerStack
cdk deploy ChunkwiseDatabaseStack
cdk deploy ChunkwiseEcsStack
```

## Accessing the Application

After deployment completes, the ALB DNS name will be output:
```bash
# Get the load balancer URL
aws cloudformation describe-stacks \
    --stack-name ChunkwiseComputeStack \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerUrl`].OutputValue' \
    --output text
```

Access the API at: `http://<alb-dns-name>/api/health`

If accessing the app from the frontend, point the frontend app to the same ALB DNS name

## Envrironment Variables

The following environment variables are configured automatically:

- `DB_HOST` - RDS endpoint
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Retrieved from Secrets Manager
- `CHUNKING_SERVICE_HOST` and `CHUNKING_SERVICE_PORT` - Cloud Map service discovery
- `EVALUATION_SERVICE_HOST` and `EVALUATION_SERVICE_PORT`- Cloud Map service discovery
- `S3_BUCKET_NAME` - S3 bucket for documents
- `OPENAI_API_KEY` - Retrieved from Secrets Manager

## Useful CDK Commands
```bash
# List all stacks
cdk ls

# View differences before deploying
cdk diff

# Synthesize CloudFormation template
cdk synth ChunkwiseNetworkStack

# View what will be deployed
cdk deploy --all --dry-run
```

## Destroying the Deployment

**⚠️ Warning: This will delete all resources and data. This action cannot be undone.**

### Destroy Stacks in the Following Order
```bash
# 1. Destroy ECS stack first
cdk destroy ChunkwiseEcsStack

# 2. Destroy other stacks
cdk destroy --all