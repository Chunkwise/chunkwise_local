# CDK deployment for Chunkwise

This CDK application automates the deployment of Chunkwise, a chunking evaluation platform and a RAG data ingestion pipeline, to AWS.

⚠️ **Important - Production configuration**:

- The application is configured for **PRODUCTION** by default, where databases and S3 bucket have `RemovalPolicy.RETAIN` to prevent accidental data loss. On data stack deletion, these resources will be **RETAINED** and continue to incur costs. Manual cleanup is required for full decommission.
- For **DEVELOPMENT/TESTING**, set `ENVIRONMENT = "development"` in `config.py` to enable automatic cleanup.

## Environment modes

### Production mode (Default - Current configuration)

- ✅ Databases and S3 are **RETAINED** on deletion of the Data stack for data protection
- ✅ Deletion protection enabled on databases
- ⚠️ Retained resources continue to incur costs
- ⚠️ Manual cleanup required when fully decommissioning

### Development mode

- ✅ All esources are **DESTROYED** on stack deletion (clean teardown)
- ✅ Lower costs, easy iteration, no orphaned resources
- 🔧 Set `ENVIRONMENT = "development"` in `config.py` before deployment

## Architecture overview

The deployment creates:

### Chunking experimentation platform

- **VPC**: Custom VPC with public and private subnets across 2 availability zones
- **ECS Fargate**: Three containerized microservices (server, chunking, evaluation)
- **RDS PostgreSQL**: Relational database that stores chunking visualization and evaluation results
- **S3**: Stores documents to evaluate and LLM-generated queries
- **Application Load Balancer**: Routes external traffic to the server service
- **AWS Cloud Map**: Service discovery for inter-service communication

### RAG data ingestion pipeline

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

2. **Python 3.7+** installed

3. **Node.js 22.x+ and npm** installed

4. **AWS CDK** installed globally

    ```bash
      npm install -g aws-cdk
    ```

5. **OpenAI API Key** stored in AWS Secrets Manager (see below)

## Initial setup

### 1. Clone the Repository

```bash
git clone https://github.com/Chunkwise/chunkwise.git
cd chunkwise/cdk
```

### 2. Configure environment mode

**For production deployment (default):**

- No changes needed - already configured for production

**For development/testing:**

```python
# Edit config.py
ENVIRONMENT = "development"  # Change from "production"
```

### 3. Create Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Bootstrap CDK (First time only)

If this is your first time using CDK in your AWS account/region:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

Example:

```bash
cdk bootstrap aws://123456789012/us-west-2
```

### 6. Store OpenAI API key in Secrets Manager

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

## Deployment

### Option 1: Deploy all stacks at once (Recommended)

```bash
cdk deploy --all
```

This will deploy all four stacks:

1. `ChunkwiseNetworkStack` - VPC with public/private subnets across 2 availability zones, NAT gateways, Internet gateway
2. `ChunkwiseLoadBalancerStack` - Application Load Balancer, target group, and security group
3. `ChunkwiseDataStack` - 2 RDS PostgreSQL instances (evaluation + production with pgvector), subnet group, security groups, Secrets Manager secrets for database credentials, 1 S3 bucket
4. `ChunkwiseEcsStack` - ECS cluster, 3 services (server, chunking, evaluation), Cloud Map, IAM roles, CloudWatch log groups, security groups, Secrets Manager secrets for API key
5. `ChunkwiseBatchStack` - AWS Batch compute environment, job queue, job definition, IAM roles

### Option 2: Deploy stacks individually

```bash
cdk deploy ChunkwiseNetworkStack
cdk deploy ChunkwiseLoadBalancerStack
cdk deploy ChunkwiseDataStack
cdk deploy ChunkwiseEcsStack
cdk deploy ChunkwiseBatchStack
```

## Accessing the application

After the load balancer stack deploys, the ALB DNS name will be output:

```bash
# Get the load balancer URL
aws cloudformation describe-stacks \
    --stack-name ChunkwiseLoadBalancerStack \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text
```

Test the API at: `http://<alb-dns-name>/api/health`
Expected response: {"status":"ok"}

Connect frontend: point the frontend application to `http://<alb-dns-name>`

## Destroying the deployment

⚠️ **Warning: Destruction behavior depends on your environment configuration**

### Current Ccnfiguration: Production mode

When you destroy stacks in production mode, resources are separated into two categories:

#### ✅ **Application stacks** (Safe to Destroy - Automatically Removed)

- **ECS Stack**: ECS services, tasks, and cluster
- **Load Balancer Stack**: Application Load Balancer and target groups
- **Batch Stack**: AWS Batch compute environment, job queues, and job definitions
- CloudWatch log groups (depending on retention settings)

These stacks can be destroyed and redeployed as needed without data loss.

#### ❌ **Foundation stacks** (RETAINED - Manual Cleanup Required)

- **Network Stack**: VPC, subnets, NAT gateways, internet gateway, route tables
- **Data Stack**: RDS instances (evaluation + production), DB subnet groups, DB security groups, S3 bucket
- Secrets: Database credentials, OpenAI API key

**These resources will continue to incur costs after stack destruction.**

### Destruction steps (Production mode)

1. Destroy the application stacks in the following order

    ```bash
    # Destroy ECS stack first
    cdk destroy ChunkwiseEcsStack

    # Destroy Load Balancer and Batch stacks
    cdk destroy ChunkwiseLoadBalancerStack
    cdk destroy ChunkwiseBatchStack
    ```

2. Before destroying foundation stacks, export or back up data

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
    # Now destroy the data stack (resources already manually deleted)
    cdk destroy ChunkwiseDataStack

    # Finally destroy the network stack
    cdk destroy ChunkwiseNetworkStack
    ```

### Destruction steps (Development mode)

If you're running in development mode (`ENVIRONMENT = "development"` in `config.py`):

1. Destroy the stacks in the following order

    ```bash
    # Destroy ECS stack first
    cdk destroy ChunkwiseEcsStack

    # Destroy all other stacks
    cdk destroy --all
    ```

2. Manually destroy the OpenAI API key in Secrets Manager as it's not managed by the CDK app
