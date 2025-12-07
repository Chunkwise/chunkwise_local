#!/usr/bin/env python3
import os
import warnings
import json

warnings.filterwarnings(
    "ignore", message="Typeguard cannot check the", category=UserWarning
)
os.environ["PYTHON_TYPE_CHECKING_DISABLE"] = "1"

import aws_cdk as cdk
from stacks.network_stack import NetworkStack
from stacks.data_stack import DataStack
from stacks.ecs_stack import EcsStack
from stacks.load_balancer_stack import LoadBalancerStack
from stacks.batch_stack import BatchStack


app = cdk.App()

# CDK now expects a json string as context
options = app.node.try_get_context("options")
if options:
    OPTIONS_JSON = json.loads(options)

    if not isinstance(OPTIONS_JSON, dict):
        raise AttributeError("Must provide an options in JSON format")
else:
    OPTIONS_JSON = None


# Get environment variables or use defaults, for the reason use the one passed in as context
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=(OPTIONS_JSON and OPTIONS_JSON.get("region"))
    or os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
)

# Stack 1: Network Infrastructure (VPC, Subnets, NAT Gateways, etc.)
network_stack = NetworkStack(
    app,
    "ChunkwiseNetworkStack",
    env=env,
    description="Chunkwise Network Infrastructure - VPC, Subnets, NAT Gateways",
)

# Stack 2: Data Layer (RDS Instances (Evaluation and Production), S3 Bucket)
data_stack = DataStack(
    app,
    "ChunkwiseDataStack",
    vpc=network_stack.vpc,
    env=env,
    description="Chunkwise Data Layer - RDS PostgreSQL Instances and S3 Bucket",
)

# Stack 3: ECS Cluster and Services
ecs_stack = EcsStack(
    app,
    "ChunkwiseEcsStack",
    vpc=network_stack.vpc,
    database=data_stack.database,
    vector_database=data_stack.production_database,
    documents_bucket=data_stack.documents_bucket, 
    env=env,
    description="Chunkwise ECS Cluster and Services",
)

# Stack 4: Load Balancer
load_balancer_stack = LoadBalancerStack(
    app,
    "ChunkwiseLoadBalancerStack",
    vpc=network_stack.vpc,
    server_service=ecs_stack.server_service,
    env=env,
    description="Chunkwise Application Load Balancer",
)

# Stack 5: AWS Batch (for production deployment workflows)
batch_stack = BatchStack(
    app,
    "ChunkwiseBatchStack",
    vpc=network_stack.vpc,
    production_database=data_stack.production_database,
    server_task_role=ecs_stack.task_role,
    env=env,
    description="Chunkwise AWS Batch - Data Ingestion Processing Workflows",
)

# Outputs
cdk.CfnOutput(
    load_balancer_stack,
    "LoadBalancerDNS",
    value=load_balancer_stack.alb.load_balancer_dns_name,
    description="Application Load Balancer DNS Name",
    export_name="ChunkwiseAlbDnsName",
)

cdk.CfnOutput(
    load_balancer_stack,
    "ApplicationUrl",
    value=f"http://{load_balancer_stack.alb.load_balancer_dns_name}",
    description="Application URL (HTTP)",
)

cdk.CfnOutput(
    batch_stack,
    "BatchJobQueue",
    value="chunkwise-job-queue",
    description="Batch Job Queue for data ingestion processing workflows",
)

cdk.CfnOutput(
    batch_stack,
    "BatchJobDefinition",
    value="chunkwise-job-definition",
    description="Batch Job Definition for data ingestion processing workflows",
)

app.synth()
