#!/usr/bin/env python3
import os
import json
import aws_cdk as cdk
from stacks.network_stack import NetworkStack
from stacks.database_stack import DatabaseStack
from stacks.ecs_stack import EcsStack
from stacks.load_balancer_stack import LoadBalancerStack

app = cdk.App()

# CDK now expects a json string as context
options = app.node.try_get_context("options")
if options:
    options_json = json.loads(options)

    if not isinstance(options_json, dict):
        raise AttributeError("Must provide an options in JSON format")
else:
    options_json = None


# Get environment variables or use defaults, for the reason use the one passed in as context
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=(options_json and options_json.get("region"))
    or os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
)

# Stack 1: Network Infrastructure (VPC, Subnets, NAT Gateways, etc.)
network_stack = NetworkStack(
    app,
    "ChunkwiseNetworkStack",
    env=env,
    description="Chunkwise Network Infrastructure - VPC, Subnets, NAT Gateways",
)

# Stack 2: Database (RDS PostgreSQL)
database_stack = DatabaseStack(
    app,
    "ChunkwiseDatabaseStack",
    vpc=network_stack.vpc,
    env=env,
    description="Chunkwise Database - RDS PostgreSQL Instance",
)

# Stack 3: ECS Cluster and Services
ecs_stack = EcsStack(
    app,
    "ChunkwiseEcsStack",
    vpc=network_stack.vpc,
    database=database_stack.database,
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


# Output the ALB DNS name
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

app.synth()
