# Chunkwise

## Overview

This repository provides everything you need to set up Chunkwise in a production environment. Chunkwise provides tools for experimenting with document chunking strategies, evaluating their effectiveness, and deploying ETL pipelines for RAG applications.

A CLI tool is included to streamline deployment and management. The `cdk/` directory contains AWS CDK infrastructure code to deploy the required AWS services: VPC, ECS Fargate, RDS PostgreSQL, S3, Application Load Balancer, AWS Batch, and Secrets Manager.

## Index

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [CLI Tool](#cli-tool)
  - [Deploying Chunkwise](#deploying-chunkwise)
  - [Destroying Chunkwise](#destroying-chunkwise)
- [AWS CDK](#aws-cdk)
  - [Environment Modes](#environment-modes)
  - [Initial Setup](#initial-setup)
  - [Deployment](#deployment)
  - [Accessing the Application](#accessing-the-application)
  - [Destroying the Deployment](#destroying-the-deployment)
- [File Structure](#file-structure)

## Architecture

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

## Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.7+
- Node.js 22.x+ and npm
- Poetry (Python package manager)
- OpenAI API Key

## Getting started

```bash
git clone https://github.com/Chunkwise/chunkwise.git
cd chunkwise/cli
poetry install
eval $(poetry env activate)
```

## CLI tool

The CLI provides an interactive deployment interface that handles all setup automatically.

### Deploying Chunkwise

```bash
typer cli.py run deploy
```

This command gathers configuration, installs dependencies, creates secrets, bootstraps CDK, and deploys all AWS stacks.

After deployment, build and run the client:

```bash
typer cli.py run client-run [--region=REGION]
```

Pass `--region` if deployed to a non-default region.

**Additional Commands:**

| Command                                           | Description                                                       |
| ------------------------------------------------- | ----------------------------------------------------------------- |
| `typer cli.py run client-build [--region=REGION]` | Builds the React client only. ALB DNS is retrieved automatically. |
| `typer cli.py run client-start`                   | Starts a previously built client using Vite. Stop with `Ctrl+C`.  |

### Destroying Chunkwise

```bash
typer cli.py run destroy [--region=REGION]
```

Destruction behavior depends on environment mode (set in `cdk/config.py`):

- **Development mode**: Removes all stacks and secrets completely.
- **Production mode**: Retains data layer (RDS, S3) to prevent data loss.

To permanently delete retained production data:

```bash
typer cli.py run destroy-data [--region=REGION]
```

Requires typing `DELETE DATA` to confirm. This deletes RDS instances, S3 bucket, and secrets.

## AWS CDK

The `cdk/` directory contains AWS CDK infrastructure code for deploying Chunkwise to AWS.

### Environment modes

⚠️ **Important**: The application runs in **production mode by default**.

#### Production mode (Default)

- Deletion protection enabled on RDS instances
- On stack deletion, data resources are **retained** and continue to incur costs
- Manual cleanup is required for full decommission

#### Development mode

- All resources are **destroyed** on stack deletion
- Lower costs, easy iteration, no orphaned resources
- Enable by setting `ENVIRONMENT = "development"` in `cdk/config.py` before deployment

### Initial setup

#### 1. Clone the repository

```bash
git clone https://github.com/Chunkwise/chunkwise.git
cd chunkwise/cdk
```

#### 2. Configure environment mode (Optional)

For development/testing only:

```python
# Edit cdk/config.py
ENVIRONMENT = "development"  # Change from "production"
```

#### 3. Create python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
```

#### 4. Bootstrap CDK (First time only)

Required once per AWS account/region:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

Example:

```bash
cdk bootstrap aws://123456789012/us-west-2
```

#### 5. Store OpenAI API key in Secrets Manager

```bash
aws secretsmanager create-secret \
    --name chunkwise/openai-api-key \
    --description "OpenAI API key for Chunkwise chunking and evaluation service" \
    --secret-string "sk-your-openai-api-key-here"
```

Verify the secret was created:

```bash
aws secretsmanager describe-secret --secret-id chunkwise/openai-api-key
```

### Deployment

#### Deploy all stacks (Recommended)

```bash
cdk deploy --all
```

This deploys five stacks in order:

1. **ChunkwiseNetworkStack**: VPC with public/private subnets across 2 AZs, NAT gateways, Internet gateway, route tables
2. **ChunkwiseLoadBalancerStack**: Application Load Balancer, target group, security group for ingress traffic
3. **ChunkwiseDataStack**: 2 RDS PostgreSQL instances (evaluation + production with pgvector), DB subnet group, security groups, Secrets Manager secrets for database credentials, S3 bucket for documents
4. **ChunkwiseEcsStack**: ECS Fargate cluster, 3 services (server, chunking, evaluation), Cloud Map namespace for service discovery, IAM roles, CloudWatch log groups
5. **ChunkwiseBatchStack**: AWS Batch compute environment, job queue, job definition for document processing

#### Deploy stacks individually

```bash
cdk deploy ChunkwiseNetworkStack
cdk deploy ChunkwiseLoadBalancerStack
cdk deploy ChunkwiseDataStack
cdk deploy ChunkwiseEcsStack
cdk deploy ChunkwiseBatchStack
```

### Accessing the application

Get the load balancer URL:

```bash
aws cloudformation describe-stacks \
    --stack-name ChunkwiseLoadBalancerStack \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text
```

- Health check: `http://<alb-dns-name>/api/health` → Expected: `{"status":"ok"}`
- Frontend: Point the client application to `http://<alb-dns-name>`

### Destroying the deployment

#### Destroying in development mode

```bash
cdk destroy ChunkwiseEcsStack
cdk destroy --all
```

Then manually delete the OpenAI API key (not managed by CDK):

```bash
aws secretsmanager delete-secret \
    --secret-id chunkwise/openai-api-key \
    --force-delete-without-recovery
```

#### Destroying in production mode

1. Destroy application stacks (safe, no data loss):

   ```bash
   # Destroy ECS stack first
   cdk destroy ChunkwiseEcsStack

   # Destroy Load Balancer and Batch stacks
   cdk destroy ChunkwiseLoadBalancerStack
   cdk destroy ChunkwiseBatchStack
   ```

2. Back up data if needed. Export any data from RDS or S3 before proceeding.

3. Manually delete retained data resources via AWS Console:

   - Disable deletion protection on both RDS instances
   - Delete both RDS instances (evaluation + production)
   - Empty and delete the S3 bucket (chunkwise-\*)

4. Delete secrets:

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

5. Destroy foundation stacks:

   ```bash
   cdk destroy ChunkwiseDataStack
   cdk destroy ChunkwiseNetworkStack
   ```

## File Structure

```text
chunkwise/
├── cdk/                    # AWS CDK infrastructure
│   ├── app.py              # CDK app entry point
│   ├── config.py           # Environment configuration
│   └── stacks/             # Stack definitions
│       ├── batch_stack.py
│       ├── data_stack.py
│       ├── ecs_stack.py
│       ├── load_balancer_stack.py
│       └── network_stack.py
├── chunking/               # Chunking service
│   ├── Dockerfile
│   ├── main.py
│   └── get_chunks_with_metadata.py
├── cli/                    # Command line interface
│   └── cli.py
├── client/                 # React frontend
│   ├── src/
│   ├── index.html
│   └── vite.config.ts
├── evaluation/             # Evaluation service
│   ├── Dockerfile
│   ├── main.py
│   └── services/
├── processing/             # Document processing for AWS Batch
│   ├── Dockerfile
│   ├── process_document.py
│   ├── config.py
│   └── services.py
└── server/                 # Main API server
    ├── Dockerfile
    ├── main.py
    ├── config/
    ├── server_types/
    ├── services/
    └── utils/
```
