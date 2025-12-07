# Chunkwise CDK Deployment

This CDK application automates the production deployment of Chunkwise, a document chunking evaluation platform and a RAG data ingestion pipeline, to AWS.

⚠️ **Important - Production Configuration** ⚠️:

- The application is configured for **PRODUCTION** by default, where databases and S3 bucket have `RemovalPolicy.RETAIN` to prevent accidental data loss. On data stack deletion, these resources will be **RETAINED** and continue to incur costs. Manual cleanup is required for full decommission.
- For **DEVELOPMENT/TESTING**, set `ENVIRONMENT = "development"` in `config.py` to enable automatic cleanup.

## Environment Modes

### Production Mode (Default - Current Configuration)

- ✅ Databases and S3 are **RETAINED** on deletion of the Data stack for data protection
- ✅ Deletion protection enabled on databases
- ⚠️ Retained resources continue to incur costs
- ⚠️ Manual cleanup required when fully decommissioning

### Development Mode

- ✅ Resources are **DESTROYED** on stack deletion (clean teardown)
- ✅ Lower costs, easy iteration, no orphaned resources
- 🔧 Set `ENVIRONMENT = "development"` in `config.py` before deployment

## Architecture Overview

The deployment creates:

**Chunking evaluation platform**

- **VPC**: Custom VPC with public and private subnets across 2 availability zones
- **ECS Fargate**: Three containerized microservices (server, chunking, evaluation)
- **RDS PostgreSQL**: Relational database that stores chunking visualization and evaluation results
- **S3**: Stores documents to evaluate and LLM-generated queries
- **Application Load Balancer**: Routes external traffic to the server service
- **AWS Cloud Map**: Service discovery for inter-service communication

**RAG Data Ingestion Pipeline**

- **AWS Batch**: On-demand document processing for production deployments, which uses
- **Fargate compute environment** to process documents in parallel:
  Normalizes, chunks, and embeds documents into vector database
- **RDS PostgreSQL with pgvector**: Vector database that stores chunked documents and embeddings for deployed workflows using a specific chunking strategy

- **CloudWatch**: Centralized logging for monitoring all services
- **Secrets Manager**: Stores database credentials and API key for all services

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

### 2. Configure Environment Mode

**For production deployment (default):**

- No changes needed - already configured for production

**For development/testing:**

```python
# Edit config.py
ENVIRONMENT = "development"  # Change from "production"
```

### 3. Create Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Bootstrap CDK (First Time Only)

If this is your first time using CDK in your AWS account/region:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

Example:

```bash
cdk bootstrap aws://123456789012/us-west-2
```

### 6. Store OpenAI API Key in Secrets Manager

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

### 7. Review `config.py` and Adjust Configuration

**Environment setting:**

```python
ENVIRONMENT = "production"  # Default - retains data on deletion
# ENVIRONMENT = "development"  # Destroys all resources on deletion
```

**Resource allocation and configuration:**

- Default configuration uses AWS Free Tier eligible resources
- For production workloads, consider upgrading instance types

**Docker images:**
If you want to use your own images, update the image URIs (from ECR):

```python
DOCKER_IMAGES = {
    "server": "123456789012.dkr.ecr.us-east-1.amazonaws.com/chunkwise-server:latest",
    "chunking": "123456789012.dkr.ecr.us-east-1.amazonaws.com/chunkwise-chunking:latest",
    "evaluation": "123456789012.dkr.ecr.us-east-1.amazonaws.com/chunkwise-evaluation:latest"
    "processing": "123456789012.dkr.ecr.us-east-1.amazonaws.com/chunkwise-processing:latest"
}
```

## Deployment

### Option 1: Deploy All Stacks at Once (Recommended)

```bash
cdk deploy --all
```

This will deploy all four stacks:

1. `ChunkwiseNetworkStack` - VPC with public/private subnets across 2 availability zones, NAT gateways, Internet gateway
2. `ChunkwiseLoadBalancerStack` - Application Load Balancer, target group, and security group
3. `ChunkwiseDataStack` - 2 RDS PostgreSQL instances (evaluation + production with pgvector), subnet group, security groups, Secrets Manager secrets for database credentials, 1 S3 bucket
4. `ChunkwiseEcsStack` - ECS cluster, 3 services (server, chunking, evaluation), Cloud Map, IAM roles, CloudWatch log groups, security groups, Secrets Manager secrets for API key
5. `ChunkwiseBatchStack` - AWS Batch compute environment, job queue, job definition, IAM roles

### Option 2: Deploy Stacks Individually

```bash
cdk deploy ChunkwiseNetworkStack
cdk deploy ChunkwiseLoadBalancerStack
cdk deploy ChunkwiseDataStack
cdk deploy ChunkwiseEcsStack
cdk deploy ChunkwiseBatchStack
```

## Accessing the Application

After the load balancer stack deploys, the ALB DNS name will be output:

```bash
# Get the load balancer URL
aws cloudformation describe-stacks \
    --stack-name ChunkwiseComputeStack \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerUrl`].OutputValue' \
    --output text
```

Test the API at: `http://<alb-dns-name>/api/health`
Expected response: {"status":"ok"}

Connect Frontend: point the frontend application to `http://<alb-dns-name>`

## Envrironment Variables

The following environment variables are configured automatically by CDK:

- `DB_HOST` - Evaluation RDS endpoint
- `DB_NAME` - Evaluation Database name
- `DB_USER` - Evaluation Database username
- Evaluation Database credentials stored in Secrets Manager
- `VECTOR_DB_HOST` - Production RDS endpoint
- `VECTOR_DB_NAME` - Production Database name
- `VECTOR_DB_PORT` - Production Database port
- Production Database credentials stored in Secrets Manager
- `CHUNKING_SERVICE_HOST` and `CHUNKING_SERVICE_PORT` - Cloud Map service discovery
- `EVALUATION_SERVICE_HOST` and `EVALUATION_SERVICE_PORT`- Cloud Map service discovery
- `S3_BUCKET_NAME` - S3 bucket for storing test documents and LLM-generated queries
- `OPENAI_API_KEY` - Retrieved from Secrets Manager

Batch Processing Jobs

- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` - AWS credentials for accessing the user's S3 bucket
- `DOCUMENT_KEY` - S3 key of document to process (set per job)
- `BUCKET_NAME` - User's S3 bucket (set per job)
- `VECTOR_DB_HOST`, `VECTOR_DB_PORT`, `VECTOR_DB_NAME`, `VECTOR_DB_USER`, `VECTOR_DB_PASSWORD` - Production database connection (set per job)
- `VECTOR_DB_TABLE` - Table to write to (set per job)
- `CHUNKER_CONFIG` - Chunking configuration JSON (set per job)

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

## Updating the Deployment

**Recommended for production environment: Update in place**

```bash
cdk deploy --all
```

This updates existing resources without destroying data.

**Complete teardown** (⚠️ rarely needed - see "Destroying the Deployment" section):

- Requires manual cleanup of retained resources
- Not recommended unless fully decommissioning

## Destroying the Deployment

**⚠️ Warning: Destruction behavior depends on your environment configuration**

### Current Configuration: Production Mode

When you destroy stacks in production mode, resources are separated into two categories:

#### ✅ **Application Stacks** (Safe to Destroy - Automatically Removed)

- **ECS Stack**: ECS services, tasks, and cluster
- **Load Balancer Stack**: Application Load Balancer and target groups
- **Batch Stack**: AWS Batch compute environment, job queues, and job definitions
- CloudWatch log groups (depending on retention settings)

These stacks can be destroyed and redeployed as needed without data loss.

#### ❌ **Foundation Stacks** (RETAINED - Manual Cleanup Required)

- **Network Stack**: VPC, subnets, NAT gateways, internet gateway, route tables
- **Data Stack**: RDS instances (evaluation + production), DB subnet groups, DB security groups, S3 bucket
- Secrets: Database credentials, OpenAI API key

**These resources will continue to incur costs after stack destruction.**

### Destruction Steps (Production Mode)

#### For routine teardowns or redeployments:

1. Destroy the application stacks in the following order

```bash
# Destroy ECS stack first
cdk destroy ChunkwiseEcsStack

# Destroy Load Balancer and Batch stacks
cdk destroy ChunkwiseLoadBalancerStack
cdk destroy ChunkwiseBatchStack
```

To redeploy, run `cdk deploy --all`

#### For complete cleanup, continue with the following steps

2. Before destroying fundation stacks, export or back up data

3. Manually delete retained data resources via AWS Console

- Disable "deletion protection" for both RDS instances (evaluation + production)
- Delete both RDS instances
- Delete the S3 bucket (chunkwise-\*)

4. Delete database credentials and OpenAI API key in Secrets Manager

```bash
aws secretsmanager delete-secret \
  --secret-id chunkwise/db-credentials \
  --force-delete-without-recovery

aws secretsmanager delete-secret \
  --secret-id chunkwise/production-db-credentials \
  --force-delete-without-recovery

aws secretsmanager delete-secret \
  --secret-id chunkwise/openai-api-key \
  --force-delete-without-recovery
```

5. Destroy foundation stacks

```bash
# Now destroy the database stack (resources already manually deleted)
cdk destroy ChunkwiseDataStack

# Finally destroy the network stack
cdk destroy ChunkwiseNetworkStack
```

### Destruction Steps (Development Mode)

If you're running in development mode (`ENVIRONMENT = "development"` in `config.py`):

1. Destroy the stacks in the following order

```bash
# Destroy ECS stack first
cdk destroy ChunkwiseEcsStack

# Destroy all other stacks
cdk destroy --all
```

2. Manually destroy the OpenAI API key in Secrets Manager as it's not managed by the CDK app
