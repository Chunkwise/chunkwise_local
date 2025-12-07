import re
from pathlib import Path
import subprocess
import importlib.util
import json
import boto3
from botocore.exceptions import ClientError
import typer
from typing_extensions import Annotated
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.console import Console
from rich.table import Table


DEPLOY_RE = re.compile(
    r"^(?P<stack>[^|]+)\|\s*(?P<progress>\d+/\d+)\s*\|\s*(?P<time>[^|]+)\|\s*(?P<status>[^|]+)\|\s*(?P<type>[^|]+)\|\s*(?P<resource>.+)$"
)
DESTROY_RE = re.compile(
    r"^(?P<stack>[^|]+)\|\s*(?P<index>\d+)\s*\|\s*(?P<time>[^|]+)\|\s*(?P<status>[^|]+)\|\s*(?P<type>[^|]+)\|\s*(?P<resource>.+)$"
)

console = Console()

CDK_DIR = Path(__file__).resolve().parent.parent / "cdk"
CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"

# Load cdk/config.py dynamically
CDK_CONFIG_PATH = Path(__file__).resolve().parent.parent / "cdk" / "config.py"
spec = importlib.util.spec_from_file_location("cdk_config", CDK_CONFIG_PATH)
cdk_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cdk_config)

env = cdk_config.ENVIRONMENT.lower()  # "production" or "development"


def validate_key(key):
    """Simple validation for OpenAI API key format."""
    if not isinstance(key, str) or len(key) == 0 or not key.startswith("sk-"):
        return False
    return True


def display_logo():
    """Displays the Chunkwise logo in the terminal."""
    with open("logo.txt", encoding="utf-8") as logo_file:
        logo_text = logo_file.read()

    console.print(f"[#00BCF7]{logo_text}")

    with open("chunkwise_monospace.txt", encoding="utf-8") as name_file:
        text = name_file.read()

    console.print(f"[white]{text}")


def ensure_cdk_dependencies():
    """
    Install CDK Python dependencies if they are not installed.
    Looks for requirements.txt or pyproject.toml inside the CDK directory.
    """

    req_file = CDK_DIR / "requirements.txt"

    if req_file.exists():
        console.print("[yellow]📦 Ensuring CDK dependencies...")
        cmd = ["pip", "install", "-r", "requirements.txt"]
    else:
        console.print("[red]⚠️ No dependency file found in CDK directory.")
        return

    # Install inside the CDK directory
    proc = subprocess.Popen(
        cmd,
        cwd=CDK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    proc.wait()

    if proc.returncode != 0:
        console.print("[red]❌ CDK dependency installation failed.")
        raise typer.Exit(code=1)

    console.print("[green]✅ CDK dependencies ready!")


def ensure_npm_dependencies():
    """
    Ensures that the client-side npm dependencies are installed.
    If node_modules/ does not exist, runs `npm install` in the client directory.
    """

    node_modules = CLIENT_DIR / "node_modules"
    package_json = CLIENT_DIR / "package.json"

    if not package_json.exists():
        console.print("[yellow]⚠️ No package.json found in client directory.")
        return

    if node_modules.exists():
        console.print("[green]📦 Client NPM dependencies already installed.")
        return

    console.print("[yellow]📦 Installing NPM dependencies for client...")

    try:
        proc = subprocess.Popen(
            ["npm", "install"],
            cwd=CLIENT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        proc.wait()

        if proc.returncode != 0:
            console.print("[red]❌ NPM install failed.")
            raise typer.Exit(code=1)

    except FileNotFoundError as exc:
        console.print("[red]❌ NPM is not installed or not in PATH.")
        raise typer.Exit(code=1) from exc

    console.print("[green]✅ Client NPM dependencies ready!")


def run_cdk_command(*args):
    """
    Runs a CDK command inside the CDK directory.
    Streams output live and preserves exit codes.
    """

    console.print(f"[yellow]👉 Running: cdk {' '.join(args)} (in {CDK_DIR})")

    proc = subprocess.Popen(
        ["cdk"] + list(args),
        cwd=CDK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    with Live(console=console, refresh_per_second=10) as live:
        for raw_line in proc.stdout:
            line = raw_line.rstrip()

            # Try to parse CloudFormation event lines
            m = DEPLOY_RE.search(line) if "deploy" in args else DESTROY_RE.search(line)
            if m:
                # Extracted fields
                index = m.group(1)
                status = m.group(2)
                resource = m.group(3)

                table = Table(title="CloudFormation Progress")
                table.add_column("Stack")
                table.add_column("Status")
                table.add_column("Last update")

                table.add_row(index, status, resource)
                live.update(table)

    proc.wait()
    if proc.returncode != 0:
        raise typer.Exit(code=proc.returncode)


def run_client_command(*args):
    """
    Runs a npm command from the client directory.
    """

    console.print(f"[yellow]👉 Running: npm run {' '.join(args)} (in {CLIENT_DIR})")

    try:
        proc = subprocess.Popen(
            ["npm", "run"] + list(args),
            cwd=CLIENT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Stream output line-by-line
        for line in proc.stdout:
            print(line.rstrip())

        proc.wait()

        if proc.returncode != 0:
            raise typer.Exit(code=proc.returncode)

    except FileNotFoundError as exc:
        console.print("[red]❌ Error: Packages are not installed or not in PATH.")
        raise typer.Exit(code=1) from exc


def create_secret(secret_name, secret_value, region=None):
    """
    Runs a AWS CLI command inside to create a secret.
    """

    try:
        if not secret_name or not secret_value:
            raise ValueError("secret name and value must be provided")

        if region:
            client = boto3.client("secretsmanager", region_name=region)
        else:
            client = boto3.client("secretsmanager")

        client.create_secret(Name=secret_name, SecretString=secret_value)

        console.print(f'[green]✅ AWS Secret "{secret_name}" created!')

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceExistsException":
            console.print(f'[green]✅ Secret "{secret_name}" already exists.')
        else:
            raise


def delete_secret(secret_name, region):
    """Deletes a secret from AWS Secrets Manager."""
    if not secret_name:
        raise ValueError("secret name must be provided")

    if region:
        client = boto3.client("secretsmanager", region_name=region)
    else:
        client = boto3.client("secretsmanager")

    client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)

    console.print(f'[green]✅ AWS Secret "{secret_name}" deleted!')


def write_env_file(client_dir: str, values: dict):
    """
    Creates or updates a .env file inside the client directory.

    Args:
        client_dir (str): Path to the client folder.
        values (dict): Key/value pairs to write into .env.
    """

    client_path = Path(client_dir)
    env_path = client_path / ".env"

    # Ensure directory exists
    client_path.mkdir(parents=True, exist_ok=True)

    # Load existing variables (if .env already exists)
    existing = {}
    if env_path.exists():
        with env_path.open("r") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    existing[key] = val

    # Update with new values
    existing.update(values)

    # Write everything back
    with env_path.open("w") as f:
        for key, val in existing.items():
            f.write(f"{key}={val}\n")

    print(f"[green]✅ Successfully wrote {len(values)} values to {env_path}.")


def get_alb_dns(load_balancer_name, region=None):
    """
    Given a load balancer name return the dns.

    :param load_balancer_name: Description
    """
    if region:
        client = boto3.client("elbv2", region_name=region)
    else:
        client = boto3.client("elbv2")

    response = client.describe_load_balancers(
        Names=[
            load_balancer_name,
        ]
    )

    alb_dns = response["LoadBalancers"][0]["DNSName"]

    console.print("[green]✅ Retrieved load balancer DNS.")

    return alb_dns


app = typer.Typer()


@app.command()
def deploy():
    """
    This command displays the beautiful Chunkwise logo, then it
    gathers some information from the user which it puts into a
    JSON string to send to the AWS CDK. Finally it will trigger
    the `cdk deploy` command.
    """
    display_logo()

    openai_api_key = ""
    while not validate_key(openai_api_key):
        openai_api_key = Prompt.ask(
            "[#00BCF7]OpenAI API Key", password=True
        )  # Could make password True to hide while typing
        openai_api_key = openai_api_key.strip()
        print()

    region = Prompt.ask(
        "[#00BCF7]What region would you like to deploy Chunkwise in?",
        # Default available regions
        choices=[
            "ap-northeast-1",
            "ap-northeast-2",
            "ap-northeast-3",
            "ap-south-1",
            "ap-southeast-1",
            "ap-southeast-2",
            "ca-central-1",
            "eu-central-1",
            "eu-north-1",
            "eu-west-1",
            "eu-west-2",
            "eu-west-3",
            "sa-east-1",
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "my default",
        ],
        show_choices=False,
        default="my default",
        case_sensitive=False,
    )
    print()

    region = region.lower()

    if env == "production":
        # Add production mode warning
        console.print(
            "[yellow]⚠️  Production mode: Databases and S3 will be RETAINED on stack deletion."
        )
        console.print(
            "[yellow]   To use development mode, set ENVIRONMENT='development' in cdk/config.py."
        )
    else:
        console.print(
            "[yellow]⚠️  Development mode: Stacks and secrets will be fully destroyed on teardown."
        )
    print()

    confirm = Confirm.ask("[#00BCF7]Are you sure?")
    print()

    if not confirm:
        console.print("[red]❌ Stack deployment cancelled.")
        return

    region = None if region == "my default" else region

    options = {"region": region}
    options_json = json.dumps(options)
    account_id = boto3.client("sts").get_caller_identity().get("Account")

    ensure_cdk_dependencies()

    if region is not None:
        create_secret("chunkwise/openai-api-key", openai_api_key, region)
        run_cdk_command("bootstrap", f"aws://{account_id}/{region}")
    else:
        create_secret("chunkwise/openai-api-key", openai_api_key)
        run_cdk_command("bootstrap")

    run_cdk_command(
        "deploy",
        "--all",
        "--require-approval",
        "never",
        "-c",
        f"options={options_json}",
    )

    console.print("[green]✅ Stacks successfullly deployed.")


@app.command()
def destroy(
    region: Annotated[
        str, typer.Option(help="AWS region of the deployed stacks")
    ] = None,
):
    """
    Calls the cdk destroy command.
    """

    if env == "production":
        # Add production mode warning
        console.print(
            "[yellow]⚠️  Production mode: The following resources will be RETAINED:"
        )
        console.print("[yellow]   • Network stack (VPC, Subnets, NAT Gateways, etc.)")
        console.print(
            "[yellow]   • Data stack (2 RDS instances, S3 bucket, DB subnet group, security groups, etc.)"
        )
        console.print(
            "[yellow]   • Database credentials and OpenAI API key in Secrets Manager"
        )
        print()
        console.print(
            "[yellow]   These resources will continue to incur costs. "
            "To fully clean up, see instructions in cdk/README.md."
        )
        print()
    else:
        console.print(
            "[yellow]⚠️  Development mode: All resources will be destroyed, including secrets."
        )
        print()

    confirm = Confirm.ask("[#00BCF7]Are you sure?")
    print()

    options = {
        "region": "" if region == "my default" else region,
    }
    options_json = json.dumps(options)

    if not confirm:
        console.print("[red]❌ Stack destruction cancelled.")
        return

    ensure_cdk_dependencies()

    if env == "production":
        # Only destroy ECS, Load Balancer, and Batch stacks
        run_cdk_command(
            "destroy", "ChunkwiseEcsStack", "--force", "-c", f"options={options_json}"
        )
        run_cdk_command(
            "destroy",
            "ChunkwiseLoadBalancerStack",
            "--force",
            "-c",
            f"options={options_json}",
        )
        run_cdk_command(
            "destroy", "ChunkwiseBatchStack", "--force", "-c", f"options={options_json}"
        )

        console.print(
            "[green]✅ ECS, Load Balancer, and Batch stacks destroyed. "
            "Network and Database stacks and secrets retained."
        )
    else:
        # Destroy all stacks
        run_cdk_command(
            "destroy", "ChunkwiseEcsStack", "--force", "-c", f"options={options_json}"
        )
        run_cdk_command(
            "destroy",
            "--all",
            "--force",
            "-c",
            f"options={options_json}",
        )
        delete_secret("chunkwise/openai-api-key", region)

        console.print("[green]✅ All stacks destroyed and secrets deleted.")


@app.command()
def destroy_data(
    region: Annotated[
        str, typer.Option(help="AWS region of the deployed stacks")
    ] = None,
):
    """
    Permanently destroy all data-layer resources and the supporting network stack in PRODUCTION.

    This will:
    - Disable deletion protection on the evaluation and production RDS instances
    - Destroy the ChunkwiseDataStack (including 2 RDS instances + S3 bucket)
    - Destroy the ChunkwiseNetworkStack (VPC, subnets, NAT, etc.)
    - Delete database credentials and OpenAI API key from Secrets Manager

    WARNING: This is irreversible. Use only when you truly want to wipe data.
    """

    if env != "production":
        console.print("[yellow]⚠️  You're in development mode.")
        console.print(
            "[yellow]   Use the regular 'destroy' command instead - it will destroy everything."
        )
        return

    console.print("[red]🔥 FULL DATA RESOURCES TEARDOWN (PRODUCTION) 🔥[/red]")
    console.print("[yellow]This will attempt to permanently delete:[/yellow]")
    print("  • Evaluation RDS instance")
    print("  • Production RDS instance")
    print("  • S3 documents bucket")
    print("  • Database credentials and OpenAI API key in Secrets Manager")
    print("  • Network stack (VPC, subnets, NAT gateways, etc.)")
    print()
    console.print(
        "[yellow]This action is IRREVERSIBLE and may result in permanent data loss.[/yellow]"
    )
    print()

    # Extra safety: require exact phrase
    confirm_phrase = Prompt.ask(
        "[#00BCF7]Type 'DELETE DATA' to confirm (or anything else to cancel)"
    ).strip()

    if confirm_phrase != "DELETE DATA":
        console.print("[red]❌ Data destruction cancelled.")
        return

    region = None if region == "my default" else region

    options = {"region": region}
    options_json = json.dumps(options)

    ensure_cdk_dependencies()

    # 1) First: deploy DataStack with allow_rds_delete=true to turn off deletion protection
    console.print(
        "[yellow]👉 Step 1/4: Updating ChunkwiseDataStack to disable RDS deletion protection..."
    )
    run_cdk_command(
        "deploy",
        "ChunkwiseDataStack",
        "--require-approval",
        "never",
        "-c",
        f"options={options_json}",
        "-c",
        "allow_rds_delete=true",
    )

    # 2) Then: destroy DataStack with the same context flag
    console.print("[yellow]👉 Step 2/4: Destroying ChunkwiseDataStack (RDS + S3)...")
    run_cdk_command(
        "destroy",
        "ChunkwiseDataStack",
        "--force",
        "-c",
        f"options={options_json}",
        "-c",
        "allow_rds_delete=true",
    )

    # 3) Destroy the Network stack (now that nothing depends on it anymore)
    console.print(
        "[yellow]👉 Step 3/4: Destroying ChunkwiseNetworkStack (VPC, subnets, NAT)..."
    )
    run_cdk_command(
        "destroy",
        "ChunkwiseNetworkStack",
        "--force",
        "-c",
        f"options={options_json}",
    )

    # 4) Delete all remaining secrets (RDS credentials + OpenAI API key)
    console.print("[yellow]👉 Step 4/4: Deleting Secrets Manager entries...")

    secret_names = [
        "chunkwise/openai-api-key",
        "chunkwise/db-credentials",
        "chunkwise/production-db-credentials",
    ]

    for name in secret_names:
        try:
            delete_secret(name, region)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                console.print(f"[yellow]ℹ️ Secret '{name}' already deleted.")
            else:
                raise

    console.print(
        "[green]✅ All data, secrets, and network resources have been removed."
    )


@app.command()
def client_build(
    region: Annotated[
        str, typer.Option(help="AWS region of the deployed stacks")
    ] = None,
):
    """
    Calls the client build command.
    """
    if region:
        alb_dns = get_alb_dns("chunkwise-alb", region)
    else:
        alb_dns = get_alb_dns("chunkwise-alb")

    write_env_file("../client", {"ALB_URI": alb_dns})
    ensure_npm_dependencies()
    run_client_command("build")
    console.print("[green]✅ Client built!")


@app.command()
def client_start():
    """
    Calls the client start command.
    """
    ensure_npm_dependencies()
    run_client_command("preview")


@app.command()
def client_run(
    region: Annotated[
        str, typer.Option(help="AWS region of the deployed stacks")
    ] = None,
):
    """
    Calls the client build then client start commands
    in squence.
    """
    client_build(region)
    client_start()
