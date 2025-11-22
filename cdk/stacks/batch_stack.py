from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_batch as batch,
    aws_iam as iam,
    aws_logs as logs,
    aws_rds as rds,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct
import config


class BatchStack(Stack):
    """
    Batch Stack - Creates AWS Batch resources for processing workflows

    Resources created:
    - 1 Batch Compute Environment
    - 1 Batch Job Queue
    - 1 Batch Job Definition
    - 2 IAM Roles (Batch Execution Role, Batch Job Role)
    - 1 Security Group (for Batch tasks)
    - 1 CloudWatch Log Group
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        production_database: rds.DatabaseInstance,
        server_task_role: iam.Role,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = vpc
        self.production_database = production_database
        self.server_task_role = server_task_role

        # Create security group for Batch tasks
        self.batch_security_group = self._create_batch_security_group()

        # Create IAM roles for Batch
        self._create_batch_iam_roles()

        # Create CloudWatch log group
        self._create_log_group()

        # Create Batch resources
        self._create_compute_environment()
        self._create_job_queue()
        self._create_job_definition()

        # Grant server permission to pass Batch roles when submitting jobs
        self._grant_server_pass_role_permissions()

    def _create_batch_security_group(self) -> ec2.SecurityGroup:
        """Create security group for Batch tasks"""

        batch_sg = ec2.SecurityGroup(
            self,
            "BatchTasksSecurityGroup",
            vpc=self.vpc,
            description="Security group for Chunkwise Batch processing tasks",
            allow_all_outbound=False,  # We'll add specific rules
        )

        # Allow outbound to Production RDS
        batch_sg.add_egress_rule(
            peer=ec2.Peer.security_group_id(
                self.production_database.connections.security_groups[
                    0
                ].security_group_id
            ),
            connection=ec2.Port.tcp(config.VECTOR_RDS_CONFIG["port"]),
            description="Allow Batch tasks to connect to Production RDS",
        )

        # Allow outbound HTTPS for OpenAI API and AWS services
        batch_sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS for OpenAI API and AWS services",
        )

        # Allow Production RDS to accept connections from Batch tasks
        ec2.CfnSecurityGroupIngress(
            self,
            "ProductionRdsIngressFromBatch",
            ip_protocol="tcp",
            from_port=config.VECTOR_RDS_CONFIG["port"],
            to_port=config.VECTOR_RDS_CONFIG["port"],
            source_security_group_id=batch_sg.security_group_id,
            group_id=self.production_database.connections.security_groups[
                0
            ].security_group_id,
            description="Allow Batch tasks to connect to Production RDS",
        )

        return batch_sg

    def _create_batch_iam_roles(self):
        """Create IAM roles for Batch"""

        # Batch Job Execution Role - used by Batch to pull images and write logs
        self.batch_execution_role = iam.Role(
            self,
            "BatchExecutionRole",
            role_name="ChunkwiseBatchExecutionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                iam.ServicePrincipal("batch.amazonaws.com"),
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        # Grant access to read OpenAI secret
        openai_secret_arn = (
            f"arn:aws:secretsmanager:{self.region}:{self.account}:"
            f"secret:chunkwise/openai-api-key"
        )
        self.batch_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret",
                ],
                resources=[
                    openai_secret_arn,
                    self.production_database.secret.secret_arn,
                ],
            )
        )

        # Batch Job Role - used by the processing container at runtime
        self.batch_job_role = iam.Role(
            self,
            "BatchJobRole",
            role_name="ChunkwiseBatchJobRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # Grant S3 read access (users provide their own buckets)
        self.batch_job_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject", "s3:ListBucket"],
                resources=["*"],  # Users provide bucket names dynamically
            )
        )

        # Grant access to read secrets
        self.batch_job_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret",
                ],
                resources=[
                    openai_secret_arn,
                    self.production_database.secret.secret_arn,
                ],
            )
        )

    def _create_log_group(self):
        """Create CloudWatch log group for Batch jobs"""

        self.log_group = logs.LogGroup(
            self,
            "BatchLogGroup",
            log_group_name="/aws/batch/chunkwise-processing",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _create_compute_environment(self):
        """Create Batch compute environment"""

        # Note: We use the service-linked role for Batch
        # This is automatically created by AWS when first using Batch
        service_role_arn = (
            f"arn:aws:iam::{self.account}:role/aws-service-role/"
            f"batch.amazonaws.com/AWSServiceRoleForBatch"
        )

        self.compute_environment = batch.CfnComputeEnvironment(
            self,
            "ComputeEnvironment",
            compute_environment_name="chunkwise-compute-env",
            type="MANAGED",
            state="ENABLED",
            compute_resources={
                "type": "FARGATE",
                "maxvCpus": config.BATCH_CONFIG["max_vcpus"],
                "subnets": [subnet.subnet_id for subnet in self.vpc.private_subnets],
                "securityGroupIds": [self.batch_security_group.security_group_id],
            },
            service_role=service_role_arn,
        )

        CfnOutput(
            self,
            "ComputeEnvironmentName",
            value=self.compute_environment.compute_environment_name,
            description="Batch Compute Environment Name",
        )

    def _create_job_queue(self):
        """Create Batch job queue"""

        self.job_queue = batch.CfnJobQueue(
            self,
            "JobQueue",
            job_queue_name="chunkwise-job-queue",
            state="ENABLED",
            priority=1,
            compute_environment_order=[
                {"order": 1, "computeEnvironment": self.compute_environment.ref}
            ],
        )

        CfnOutput(
            self,
            "JobQueueName",
            value=self.job_queue.job_queue_name,
            description="Batch Job Queue Name",
            export_name="ChunkwiseBatchJobQueue",
        )

    def _create_job_definition(self):
        """Create Batch job definition"""

        self.job_definition = batch.CfnJobDefinition(
            self,
            "ProcessingJobDefinition",
            job_definition_name="chunkwise-job-definition",
            type="container",
            platform_capabilities=["FARGATE"],
            container_properties={
                "image": config.DOCKER_IMAGES["processing"],
                "resourceRequirements": [
                    {"type": "VCPU", "value": str(config.BATCH_CONFIG["job_cpu"])},
                    {"type": "MEMORY", "value": str(config.BATCH_CONFIG["job_memory"])},
                ],
                "executionRoleArn": self.batch_execution_role.role_arn,
                "jobRoleArn": self.batch_job_role.role_arn,
                "fargatePlatformConfiguration": {"platformVersion": "LATEST"},
                "runtimePlatform": {
                    "operatingSystemFamily": "LINUX",
                    "cpuArchitecture": "X86_64",
                },
                "networkConfiguration": {
                    "assignPublicIp": (
                        "ENABLED"
                        if config.BATCH_CONFIG["assign_public_ip"]
                        else "DISABLED"
                    )
                },
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": self.log_group.log_group_name,
                        "awslogs-region": self.region,
                        "awslogs-stream-prefix": "batch",
                    },
                },
                # Secrets available to all jobs (static)
                "secrets": [
                    {
                        "name": "OPENAI_API_KEY",
                        "valueFrom": (
                            f"arn:aws:secretsmanager:{self.region}:{self.account}:"
                            f"secret:chunkwise/openai-api-key"
                        ),
                    }
                ],
                # Environment variables will be provided per job via containerOverrides
                "environment": [],
            },
        )

        CfnOutput(
            self,
            "JobDefinitionArn",
            value=self.job_definition.ref,
            description="Batch Job Definition ARN",
            export_name="ChunkwiseBatchJobDefinition",
        )

    def _grant_server_pass_role_permissions(self):
        """Grant server task role permission to pass Batch roles"""

        self.server_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:PassRole"],
                resources=[
                    self.batch_execution_role.role_arn,
                    self.batch_job_role.role_arn,
                ],
                conditions={
                    "StringLike": {
                        "iam:PassedToService": [
                            "batch.amazonaws.com",
                            "ecs-tasks.amazonaws.com",
                        ]
                    }
                },
            )
        )
