import boto3
from botocore.exceptions import ClientError

rds = boto3.client("rds")


def wait_for_instance_available(db_identifier: str, timeout_sec: int = 1800):
    waiter = rds.get_waiter("db_instance_available")
    waiter.wait(
        DBInstanceIdentifier=db_identifier,
        WaiterConfig={"Delay": 15, "MaxAttempts": max(1, timeout_sec // 15)},
    )


def describe_instance(db_identifier: str):
    resp = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
    inst = resp["DBInstances"][0]
    endpoint = inst.get("Endpoint", {})
    return {
        "address": endpoint.get("Address"),
        "port": endpoint.get("Port"),
        "engine": inst.get("Engine"),
        "status": inst.get("DBInstanceStatus"),
        "db_instance_identifier": inst.get("DBInstanceIdentifier"),
        "allocated_storage": inst.get("AllocatedStorage"),
        "instance_class": inst.get("DBInstanceClass"),
        "engine_version": inst.get("EngineVersion"),
    }


def instance_exists(db_identifier: str) -> bool:
    try:
        rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
        return True
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code in (
            "DBInstanceNotFound",
            "DBInstanceNotFoundFault",
            "InvalidDBInstanceState",
        ):
            return False
        raise


def create_instance(
    db_identifier: str,
    master_username: str,
    master_password: str,
    db_name: str,
    engine: str = "postgres",
    engine_version: str = "15.4",
    db_instance_class: str = "db.t3.medium",
    allocated_storage: int = 20,
    vpc_security_group_ids: list | None = None,
    db_subnet_group_name: str | None = None,
    publicly_accessible: bool = True,
    multi_az: bool = False,
    tags: list | None = None,
):
    """
    Create an RDS instance with a DB (DBName) created at provisioning time.
    Picks engine_version explicitly to ensure pgvector support on Postgres 15.x.
    """
    params = {
        "DBInstanceIdentifier": db_identifier,
        "AllocatedStorage": allocated_storage,
        "DBInstanceClass": db_instance_class,
        "Engine": engine,
        "EngineVersion": engine_version,
        "MasterUsername": master_username,
        "MasterUserPassword": master_password,
        "DBName": db_name,
        "PubliclyAccessible": publicly_accessible,
        "MultiAZ": multi_az,
    }
    if vpc_security_group_ids:
        params["VpcSecurityGroupIds"] = vpc_security_group_ids
    if db_subnet_group_name:
        params["DBSubnetGroupName"] = db_subnet_group_name
    if tags:
        params["Tags"] = tags

    resp = rds.create_db_instance(**params)
    return resp


def create_preprovisioned_instance_if_missing(
    db_identifier: str,
    master_username: str,
    master_password: str,
    db_name: str,
    engine_version: str = "17.6",
    db_instance_class: str = "db.t4g.micro",
    allocated_storage: int = 20,
    vpc_security_group_ids: list | None = None,
    db_subnet_group_name: str | None = None,
    publicly_accessible: bool = True,
    wait_timeout: int = 1800,
):
    """
    Ensure an RDS instance exists. Create it if missing, then wait for 'available'.
    Returns describe_instance() dict when available.
    """
    if instance_exists(db_identifier):
        info = describe_instance(db_identifier)
        if info.get("status") != "available":
            wait_for_instance_available(db_identifier, timeout_sec=wait_timeout)
            info = describe_instance(db_identifier)
        return info

    # Create instance if missing
    create_instance(
        db_identifier=db_identifier,
        master_username=master_username,
        master_password=master_password,
        db_name=db_name,
        engine="postgres",
        engine_version=engine_version,
        db_instance_class=db_instance_class,
        allocated_storage=allocated_storage,
        vpc_security_group_ids=vpc_security_group_ids,
        db_subnet_group_name=db_subnet_group_name,
        publicly_accessible=publicly_accessible,
    )

    # Wait until available
    wait_for_instance_available(db_identifier, timeout_sec=wait_timeout)
    return describe_instance(db_identifier)
