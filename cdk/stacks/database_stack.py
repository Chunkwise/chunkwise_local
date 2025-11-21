from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy,
    Duration,
    CfnOutput,
)
from constructs import Construct
import config


class DatabaseStack(Stack):
    """
    Database Stack - Creates RDS PostgreSQL instance

    Resources created:
    - 1 RDS Subnet Group (shared)
    - 2 RDS Security Groups (one for each database)
    - 2 RDS PostgreSQL Instances (evaluation and production)
    - 2 Secrets (for database credentials)
    """

    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Evaluation Database (for experimentation workflows)
        self._create_evaluation_database(vpc)

        # Create Production Database (for deployment workflows)
        self._create_production_database(vpc)

    def _create_evaluation_database(self, vpc: ec2.Vpc):
        """Create the evaluation database for experimentation workflows"""

        # Create security group for Evaluation RDS
        self.db_security_group = ec2.SecurityGroup(
            self,
            "EvaluationDbSecurityGroup",
            vpc=vpc,
            description="Security group for Chunkwise Evaluation RDS PostgreSQL",
            allow_all_outbound=False,
        )

        # Create database credentials
        self.db_credentials = rds.DatabaseSecret(
            self,
            "ChunkwiseDbCredentials",
            username="postgres",
            secret_name="chunkwise/database-credentials",
        )

        # Create RDS PostgreSQL instance for evaluation
        self.database = rds.DatabaseInstance(
            self,
            "ChunkwiseEvaluationDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_17_6
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.db_security_group],
            # Database configuration
            database_name=config.RDS_CONFIG["database_name"],
            port=config.RDS_CONFIG["port"],
            credentials=rds.Credentials.from_secret(self.db_credentials),
            # Storage configuration
            allocated_storage=config.RDS_CONFIG["allocated_storage"],
            max_allocated_storage=config.RDS_CONFIG["max_allocated_storage"],
            storage_type=rds.StorageType.GP3,
            storage_encrypted=True,
            # Backup configuration
            backup_retention=Duration.days(config.RDS_CONFIG["backup_retention_days"]),
            delete_automated_backups=True,
            # High availability
            multi_az=config.RDS_CONFIG["multi_az"],
            # Public accessibility
            publicly_accessible=config.RDS_CONFIG["publicly_accessible"],
            # Deletion protection
            deletion_protection=config.RDS_CONFIG["deletion_protection"],
            # For development - allow deletion
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
            # CloudWatch monitoring
            cloudwatch_logs_exports=["postgresql"],
            enable_performance_insights=True,
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT,
        )

        # Output evaluation database endpoint
        CfnOutput(
            self,
            "EvaluationDatabaseEndpoint",
            value=self.database.instance_endpoint.hostname,
            description="Evaluation Database Endpoint",
            export_name="ChunkwiseEvaluationDbEndpoint",
        )

    def _create_production_database(self, vpc: ec2.Vpc):
        """Create the production database for deployment workflows"""

        # Create security group for Production RDS
        self.production_db_security_group = ec2.SecurityGroup(
            self,
            "ProductionDbSecurityGroup",
            vpc=vpc,
            description="Security group for Chunkwise Production RDS PostgreSQL (publicly accessible)",
            allow_all_outbound=False,
        )

        # Allow public access or restricted CIDR access
        if config.VECTOR_RDS_CONFIG["allowed_cidrs"]:
            # Restrict to specific CIDRs
            for idx, cidr in enumerate(config.VECTOR_RDS_CONFIG["allowed_cidrs"]):
                self.production_db_security_group.add_ingress_rule(
                    peer=ec2.Peer.ipv4(cidr),
                    connection=ec2.Port.tcp(config.VECTOR_RDS_CONFIG["port"]),
                    description=f"Allow PostgreSQL from {cidr}",
                )
        else:
            # Allow from anywhere (users can restrict via their own firewall)
            self.production_db_security_group.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(),
                connection=ec2.Port.tcp(config.VECTOR_RDS_CONFIG["port"]),
                description="Allow PostgreSQL from anywhere (for embedding export)",
            )

        # Create database credentials for production
        self.production_db_credentials = rds.DatabaseSecret(
            self,
            "ChunkwiseProductionDbCredentials",
            username="postgres",
            secret_name="chunkwise/production-db-credentials",
        )

        # Create RDS PostgreSQL instance for production
        self.production_database = rds.DatabaseInstance(
            self,
            "ChunkwiseProductionDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_17_6
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.production_db_security_group],
            # Database configuration
            database_name=config.VECTOR_RDS_CONFIG["database_name"],
            port=config.VECTOR_RDS_CONFIG["port"],
            credentials=rds.Credentials.from_secret(self.production_db_credentials),
            # Storage configuration
            allocated_storage=config.VECTOR_RDS_CONFIG["allocated_storage"],
            max_allocated_storage=config.VECTOR_RDS_CONFIG[
                "max_allocated_storage"
            ],
            storage_type=rds.StorageType.GP3,
            storage_encrypted=True,
            # Backup configuration
            backup_retention=Duration.days(
                config.VECTOR_RDS_CONFIG["backup_retention_days"]
            ),
            delete_automated_backups=True,
            # High availability
            multi_az=config.VECTOR_RDS_CONFIG["multi_az"],
            # Public accessibility - ENABLED for user export
            publicly_accessible=config.VECTOR_RDS_CONFIG["publicly_accessible"],
            # Deletion protection
            deletion_protection=config.VECTOR_RDS_CONFIG["deletion_protection"],
            # For development - allow deletion
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
            # CloudWatch monitoring
            cloudwatch_logs_exports=["postgresql"],
            enable_performance_insights=True,
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT,
        )

        # Output production database endpoint
        CfnOutput(
            self,
            "ProductionDatabaseEndpoint",
            value=self.production_database.instance_endpoint.hostname,
            description="Production Database Endpoint (publicly accessible)",
            export_name="ChunkwiseProductionDbEndpoint",
        )

        CfnOutput(
            self,
            "ProductionDatabasePort",
            value=str(config.VECTOR_RDS_CONFIG["port"]),
            description="Production Database Port",
        )

        CfnOutput(
            self,
            "ProductionDatabaseName",
            value=config.VECTOR_RDS_CONFIG["database_name"],
            description="Production Database Name",
        )

        CfnOutput(
            self,
            "ProductionDatabaseSecretArn",
            value=self.production_db_credentials.secret_arn,
            description="Production Database Credentials Secret ARN",
            export_name="ChunkwiseProductionDbSecretArn",
        )
