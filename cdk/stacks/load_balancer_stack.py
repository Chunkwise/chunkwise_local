from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs as ecs,
    Duration,
)
from constructs import Construct


class LoadBalancerStack(Stack):
    """
    Load Balancer Stack - Creates Application Load Balancer with HTTP listener

    Resources created:
    - 1 ALB Security Group
    - 1 Application Load Balancer
    - 1 Target Group
    - 1 HTTP Listener (port 80)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        server_service: ecs.FargateService,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create security group for ALB
        self.alb_security_group = ec2.SecurityGroup(
            self,
            "AlbSecurityGroup",
            vpc=vpc,
            description="Security group for Chunkwise Application Load Balancer",
            allow_all_outbound=True,
        )

        # Allow inbound HTTP traffic from anywhere
        self.alb_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic from anywhere",
        )

        # Create Application Load Balancer
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "ChunkwiseAlb",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="chunkwise-alb",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=self.alb_security_group,
        )

        # Create target group for server service
        self.target_group = elbv2.ApplicationTargetGroup(
            self,
            "ServerTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path="/api/health",
                protocol=elbv2.Protocol.HTTP,
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
                timeout=Duration.seconds(5),
                interval=Duration.seconds(30),
            ),
            deregistration_delay=Duration.seconds(30),
            target_group_name="chunkwise-server-tg",
        )

        # Create HTTP listener
        self.http_listener = self.alb.add_listener(
            "HttpListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_action=elbv2.ListenerAction.forward(
                target_groups=[self.target_group]
            ),
        )

        # Attach server service to target group
        server_service.attach_to_application_target_group(self.target_group)

        # Allow traffic from ALB to ECS tasks
        server_service.connections.allow_from(
            self.alb_security_group, ec2.Port.tcp(80), "Allow traffic from ALB"
        )
