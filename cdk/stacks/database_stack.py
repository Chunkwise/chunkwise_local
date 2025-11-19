from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy,
    Duration,
)
from constructs import Construct
import config


class DatabaseStack(Stack):
    """
    Database Stack - Creates RDS PostgreSQL instance

    Resources created:
    - 1 RDS Subnet Group
    - 1 RDS Security Group
    - 1 RDS PostgreSQL Instance
    - 1 Secret (for database credentials)
    """

    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create security group for RDS
        self.db_security_group = ec2.SecurityGroup(
            self,
            "RdsSecurityGroup",
            vpc=vpc,
            description="Security group for Chunkwise RDS PostgreSQL",
            allow_all_outbound=False,  # We don't need outbound from DB
        )

        # Create database credentials
        # Note: Using Secrets Manager for credentials even though we're using
        # environment variables elsewhere, as RDS requires it for master password
        self.db_credentials = rds.DatabaseSecret(
            self,
            "ChunkwiseDbCredentials",
            username="postgres",
            secret_name="chunkwise/database-credentials",
        )

        # Create RDS PostgreSQL instance
        self.database = rds.DatabaseInstance(
            self,
            "ChunkwiseDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_17_6  # or latest version
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
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
            publicly_accessible=False,  # Keep in private subnet
            # Deletion protection
            deletion_protection=config.RDS_CONFIG["deletion_protection"],
            # For development - allow deletion
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
            # CloudWatch monitoring
            cloudwatch_logs_exports=["postgresql"],
            enable_performance_insights=True,
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT,
        )
