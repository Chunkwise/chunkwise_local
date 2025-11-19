from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_servicediscovery as servicediscovery,
    aws_secretsmanager as secretsmanager,
    aws_s3 as s3,
    aws_iam as iam,
    aws_rds as rds,
    RemovalPolicy,
    Duration,
)
from constructs import Construct
import config


class EcsStack(Stack):
    """
    ECS Stack - Creates ECS Cluster, Task Definitions, Services, and Cloud Map

    Resources created:
    - 1 ECS Cluster
    - 3 ECS Task Definitions (server, chunking, evaluation)
    - 3 ECS Services
    - 1 Cloud Map Private DNS Namespace
    - 2 Cloud Map Service Discovery Services (chunking, evaluation)
    - 3 CloudWatch Log Groups
    - 1 S3 Bucket
    - 2 IAM Roles (Task Execution Role, Task Role)
    - Security Groups
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        database: rds.DatabaseInstance,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = vpc
        self.database = database

        # Create S3 bucket for document storage
        self.documents_bucket = s3.Bucket(
            self,
            "ChunkwiseDocumentsBucket",
            bucket_name=f"{config.S3_CONFIG['bucket_name_prefix']}-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
            auto_delete_objects=True,  # Only for development
        )

        # Create security group for ECS tasks
        self.ecs_security_group = ec2.SecurityGroup(
            self,
            "EcsSecurityGroup",
            vpc=vpc,
            description="Security group for Chunkwise ECS tasks",
            allow_all_outbound=True,  # Allow outbound for API calls, ECR pulls, etc.
        )

        # Create security group ingress as CloudFormation resource
        ec2.CfnSecurityGroupIngress(
            self,
            "RdsIngressFromEcs",
            ip_protocol="tcp",
            from_port=config.RDS_CONFIG["port"],
            to_port=config.RDS_CONFIG["port"],
            source_security_group_id=self.ecs_security_group.security_group_id,
            group_id=database.connections.security_groups[0].security_group_id,
            description="Allow ECS tasks to connect to RDS",
        )

        # Allow ECS tasks to communicate with each other
        self.ecs_security_group.add_ingress_rule(
            peer=self.ecs_security_group,
            connection=ec2.Port.tcp(80),
            description="Allow service-to-service communication",
        )

        # Allow ECS tasks to communicate with each other (for Cloud Map)
        self.ecs_security_group.add_ingress_rule(
            peer=self.ecs_security_group,
            connection=ec2.Port.tcp(80),
            description="Allow service-to-service communication",
        )

        # Create ECS cluster
        self.cluster = ecs.Cluster(
            self,
            "ChunkwiseCluster",
            cluster_name="chunkwise-cluster",
            vpc=vpc,
            container_insights=True,  # Enable CloudWatch Container Insights
        )

        # Create Cloud Map namespace for service discovery
        self.namespace = servicediscovery.PrivateDnsNamespace(
            self,
            "ServiceDiscoveryNamespace",
            name=config.CLOUD_MAP_CONFIG["namespace_name"],
            vpc=vpc,
            description="Private DNS namespace for Chunkwise services",
        )

        # Create IAM roles
        self._create_iam_roles()

        # Create ECS services
        self._create_chunking_service()
        self._create_evaluation_service()
        self._create_server_service()

    def _create_iam_roles(self):
        """Create IAM roles for ECS tasks"""

        # Task Execution Role - used by ECS to pull images and write logs
        self.task_execution_role = iam.Role(
            self,
            "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        # Allow reading database credentials from Secrets Manager
        self.database.secret.grant_read(self.task_execution_role)

        # Task Role - used by the application code running in containers
        self.task_role = iam.Role(
            self, "TaskRole", assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        # Grant S3 access to task role
        self.documents_bucket.grant_read_write(self.task_role)

    def _get_openai_secret(self):
        """Get reference to OpenAI API key secret"""
        if not hasattr(self, "_openai_secret"):
            self._openai_secret = secretsmanager.Secret.from_secret_name_v2(
                self, "OpenAISecret", secret_name="chunkwise/openai-api-key"
            )
            # Grant read access to task execution role
            self._openai_secret.grant_read(self.task_execution_role)
        return self._openai_secret

    def _create_log_group(self, service_name: str) -> logs.LogGroup:
        """Create CloudWatch log group for a service"""
        return logs.LogGroup(
            self,
            f"{service_name}LogGroup",
            log_group_name=f"/ecs/chunkwise-{service_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _create_chunking_service(self):
        """Create chunking service"""

        # Create log group
        log_group = self._create_log_group("Chunking")

        # Create task definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "ChunkingTaskDef",
            family="chunkwise-chunking",
            cpu=config.ECS_CONFIG["chunking"]["cpu"],
            memory_limit_mib=config.ECS_CONFIG["chunking"]["memory_limit_mib"],
            task_role=self.task_role,
            execution_role=self.task_execution_role,
        )

        # Add container
        container = task_definition.add_container(
            "chunking",
            image=ecs.ContainerImage.from_registry(config.DOCKER_IMAGES["chunking"]),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="chunking", log_group=log_group
            ),
            secrets={
                "OPENAI_API_KEY": ecs.Secret.from_secrets_manager(
                    self._get_openai_secret()
                ),
            },
            environment={
                "S3_BUCKET_NAME": self.documents_bucket.bucket_name,
            },
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "curl -f http://localhost:80/health || exit 1"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )

        container.add_port_mappings(
            ecs.PortMapping(
                container_port=config.ECS_CONFIG["chunking"]["container_port"],
                protocol=ecs.Protocol.TCP,
            )
        )

        # Create service with service discovery
        self.chunking_service = ecs.FargateService(
            self,
            "ChunkingService",
            cluster=self.cluster,
            task_definition=task_definition,
            desired_count=config.ECS_CONFIG["chunking"]["desired_count"],
            service_name="chunkwise-chunking-service",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.ecs_security_group],
            cloud_map_options=ecs.CloudMapOptions(
                cloud_map_namespace=self.namespace,
                name=config.CLOUD_MAP_CONFIG["services"]["chunking"],
                dns_record_type=servicediscovery.DnsRecordType.A,
                dns_ttl=Duration.seconds(60),
            ),
        )

    def _create_evaluation_service(self):
        """Create evaluation service"""

        # Create log group
        log_group = self._create_log_group("Evaluation")

        # Create task definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "EvaluationTaskDef",
            family="chunkwise-evaluation",
            cpu=config.ECS_CONFIG["evaluation"]["cpu"],
            memory_limit_mib=config.ECS_CONFIG["evaluation"]["memory_limit_mib"],
            task_role=self.task_role,
            execution_role=self.task_execution_role,
        )

        # Add container
        container = task_definition.add_container(
            "evaluation",
            image=ecs.ContainerImage.from_registry(config.DOCKER_IMAGES["evaluation"]),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="evaluation", log_group=log_group
            ),
            secrets={
                "OPENAI_API_KEY": ecs.Secret.from_secrets_manager(
                    self._get_openai_secret()
                ),
            },
            environment={
                "S3_BUCKET_NAME": self.documents_bucket.bucket_name,
            },
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "curl -f http://localhost:80/health || exit 1"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )

        container.add_port_mappings(
            ecs.PortMapping(
                container_port=config.ECS_CONFIG["evaluation"]["container_port"],
                protocol=ecs.Protocol.TCP,
            )
        )

        # Create service with service discovery
        self.evaluation_service = ecs.FargateService(
            self,
            "EvaluationService",
            cluster=self.cluster,
            task_definition=task_definition,
            desired_count=config.ECS_CONFIG["evaluation"]["desired_count"],
            service_name="chunkwise-evaluation-service",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.ecs_security_group],
            cloud_map_options=ecs.CloudMapOptions(
                cloud_map_namespace=self.namespace,
                name=config.CLOUD_MAP_CONFIG["services"]["evaluation"],
                dns_record_type=servicediscovery.DnsRecordType.A,
                dns_ttl=Duration.seconds(60),
            ),
        )

    def _create_server_service(self):
        """Create server (orchestrator) service"""

        # Create log group
        log_group = self._create_log_group("Server")

        # Create task definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "ServerTaskDef",
            family="chunkwise-server",
            cpu=config.ECS_CONFIG["server"]["cpu"],
            memory_limit_mib=config.ECS_CONFIG["server"]["memory_limit_mib"],
            task_role=self.task_role,
            execution_role=self.task_execution_role,
        )

        # Add container
        container = task_definition.add_container(
            "server",
            image=ecs.ContainerImage.from_registry(config.DOCKER_IMAGES["server"]),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="server", log_group=log_group
            ),
            secrets={
                # Load database credentials from Secrets Manager
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                    self.database.secret, "password"
                ),
                "DB_USER": ecs.Secret.from_secrets_manager(
                    self.database.secret, "username"
                ),
                "OPENAI_API_KEY": ecs.Secret.from_secrets_manager(
                    self._get_openai_secret()
                ),
            },
            environment={
                "DB_HOST": self.database.instance_endpoint.hostname,
                "DB_NAME": config.RDS_CONFIG["database_name"],
                "DB_PORT": str(config.RDS_CONFIG["port"]),
                "S3_BUCKET_NAME": self.documents_bucket.bucket_name,
                # Service discovery endpoints
                "CHUNKING_SERVICE_HOST": f"{config.CLOUD_MAP_CONFIG['services']['chunking']}.{config.CLOUD_MAP_CONFIG['namespace_name']}",
                "CHUNKING_SERVICE_PORT": "80",
                "EVALUATION_SERVICE_HOST": f"{config.CLOUD_MAP_CONFIG['services']['evaluation']}.{config.CLOUD_MAP_CONFIG['namespace_name']}",
                "EVALUATION_SERVICE_PORT": "80",
            },
            health_check=ecs.HealthCheck(
                command=[
                    "CMD-SHELL",
                    "curl -f http://localhost:80/api/health || exit 1",
                ],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )

        container.add_port_mappings(
            ecs.PortMapping(
                container_port=config.ECS_CONFIG["server"]["container_port"],
                protocol=ecs.Protocol.TCP,
            )
        )

        # Create service (no service discovery - will be accessed via ALB)
        self.server_service = ecs.FargateService(
            self,
            "ServerService",
            cluster=self.cluster,
            task_definition=task_definition,
            desired_count=config.ECS_CONFIG["server"]["desired_count"],
            service_name="chunkwise-server-service",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.ecs_security_group],
        )
