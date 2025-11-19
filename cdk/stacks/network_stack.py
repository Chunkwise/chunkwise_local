from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct
import config


class NetworkStack(Stack):
    """
    Network Stack - Creates VPC, Subnets, NAT Gateways, Internet Gateway

    Resources created:
    - 1 VPC with DNS support
    - 2 Public Subnets (one per AZ)
    - 2 Private Subnets (one per AZ)
    - 1 Internet Gateway
    - 2 NAT Gateways (one per public subnet)
    - 2 Elastic IPs (for NAT Gateways)
    - Route Tables (1 public, 2 private)
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with public and private subnets across 2 AZs
        self.vpc = ec2.Vpc(
            self,
            "ChunkwiseVpc",
            vpc_name="chunkwise-vpc",
            ip_addresses=ec2.IpAddresses.cidr(config.VPC_CONFIG["cidr"]),
            max_azs=config.VPC_CONFIG["max_azs"],
            nat_gateways=config.VPC_CONFIG["nat_gateways"],
            # Subnet configuration
            subnet_configuration=[
                # Public subnets - for ALB and NAT Gateways
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=20,
                ),
                # Private subnets - for ECS tasks and RDS
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=20,
                ),
            ],
            # Enable DNS
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

        # Note: Internet Gateway, NAT Gateways, Elastic IPs, and Route Tables
        # are automatically created by the VPC construct based on the configuration above
