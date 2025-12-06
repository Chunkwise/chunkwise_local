import json
import boto3
from botocore.exceptions import ClientError
import typer
from typing_extensions import Annotated
from rich import print
from rich.pretty import pprint
from rich.prompt import Prompt, Confirm, InvalidResponse
from rich.live import Live
from rich.console import Console
from rich.table import Table
import re
from pathlib import Path
import subprocess


DEPLOY_RE = re.compile(
    r"^(?P<stack>[^|]+)\|\s*(?P<progress>\d+/\d+)\s*\|\s*(?P<time>[^|]+)\|\s*(?P<status>[^|]+)\|\s*(?P<type>[^|]+)\|\s*(?P<resource>.+)$"
)
DESTROY_RE = re.compile(
    r"^(?P<stack>[^|]+)\|\s*(?P<index>\d+)\s*\|\s*(?P<time>[^|]+)\|\s*(?P<status>[^|]+)\|\s*(?P<type>[^|]+)\|\s*(?P<resource>.+)$"
)

console = Console()

CDK_DIR = Path(__file__).resolve().parent.parent / "cdk"
CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"


def validate_key(key):
    if not isinstance(key, str) or len(key) == 0 or not key.startswith("sk-"):
        return False
    return True


def display_logo():
    with open("logo.txt") as logo_file:
        logo_text = logo_file.read()

    print(f"[#00BCF7]{logo_text}")

    with open("chunkwise_monospace.txt") as name_file:
        text = name_file.read()

    print(f"[white]{text}")


def ensure_cdk_dependencies():
    """
    Install CDK Python dependencies if they are not installed.
    Looks for requirements.txt or pyproject.toml inside the CDK directory.
    """

    req_file = CDK_DIR / "requirements.txt"

    if req_file.exists():
        print(f"[yellow]📦 Ensuring CDK dependencies...")
        cmd = ["pip", "install", "-r", "requirements.txt"]
    else:
        print(f"[red]⚠️ No dependency file found in CDK directory.")
        return

    # Install inside the CDK directory
    proc = subprocess.Popen(
        cmd,
        cwd=CDK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Print the output to the console
    # for line in proc.stdout:
    #     typer.echo(line.rstrip())

    proc.wait()

    if proc.returncode != 0:
        print(f"[red]❌ CDK dependency installation failed.")
        raise typer.Exit(code=1)

    print(f"[green]✅ CDK dependencies ready!")


def ensure_npm_dependencies():
    """
    Ensures that the client-side npm dependencies are installed.
    If node_modules/ does not exist, runs `npm install` in the client directory.
    """

    node_modules = CLIENT_DIR / "node_modules"
    package_json = CLIENT_DIR / "package.json"

    if not package_json.exists():
        print(f"[yellow]⚠️ No package.json found in client directory.")
        return

    if node_modules.exists():
        print(f"[green]📦 Client NPM dependencies already installed.")
        return

    print(f"[yellow]📦 Installing NPM dependencies for client...")

    try:
        proc = subprocess.Popen(
            ["npm", "install"],
            cwd=CLIENT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Log output to the console
        # for line in proc.stdout:
        #     typer.echo(line.rstrip())

        proc.wait()

        if proc.returncode != 0:
            print(f"[red]❌ NPM install failed.")
            raise typer.Exit(code=1)

    except FileNotFoundError:
        print(f"[red]❌ NPM is not installed or not in PATH.")
        raise typer.Exit(code=1)

    print(f"[green]✅ Client NPM dependencies ready!")


def run_cdk_command(*args):
    """
    Runs a CDK command inside the CDK directory.
    Streams output live and preserves exit codes.
    """

    print(f"[yellow]👉 Running: cdk {' '.join(args)} (in {CDK_DIR})")

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
            else:
                # For non-event lines, just print normally
                # console.print(line)
                pass

    proc.wait()
    if proc.returncode != 0:
        raise typer.Exit(code=proc.returncode)


def run_client_command(*args):
    """
    Runs a npm command from the client directory.
    """

    print(f"[yellow]👉 Running: npm run {' '.join(args)} (in {CLIENT_DIR})")

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

    except FileNotFoundError:
        print(f"[red]❌ Error: Packages are not installed or not in PATH.")
        raise typer.Exit(code=1)


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

        print(f"[green]✅ AWS Secret created!")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceExistsException":
            print(f"[green]✅ Secret already exists")
        else:
            raise


def delete_secret(secret_name, region):
    if not secret_name:
        raise ValueError("secret name must be provided")

    if region:
        client = boto3.client("secretsmanager", region_name=region)
    else:
        client = boto3.client("secretsmanager")

    client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)

    print(f'[green]✅ AWS Secret "{secret_name}" deleted!')


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

    print(f"[green]✅ Successfully wrote {len(values)} values to {env_path}")


def get_alb_dns(load_balancer_name, region=None):
    """
    Given a load balancer name return the dns.

    :param load_balancer_name: Description
    """
    if region:
        client = boto3.client("elbv2", region_name=region)
    else:
        client = boto3.client("elbv2")

    # print(client.describe_load_balancers())

    response = client.describe_load_balancers(
        Names=[
            load_balancer_name,
        ]
    )

    alb_dns = response["LoadBalancers"][0]["DNSName"]

    print(f"[green]✅ Retrieved load balancer DNS")

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
            f"[#00BCF7]OpenAI API Key", password=True
        )  # Could make password True to hide while typing
        openai_api_key = openai_api_key.strip()
        print()

    region = Prompt.ask(
        f"[#00BCF7]What region would you like to deploy Chunkwise in?",
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

    region = str.lower(region)

    confirm = Confirm.ask(f"[#00BCF7]Are you sure?")
    print()

    if confirm:
        options = {
            "region": "" if region == "my default" else region,
        }
        options_json = json.dumps(options)
        account_id = boto3.client("sts").get_caller_identity().get("Account")

        ensure_cdk_dependencies()

        if region != "my default":
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

        print(f"[green]✅ Stacks successfullly deployed")
    else:
        print(f"[red]❌ Stack deployment cancelled")


@app.command()
def destroy(
    region: Annotated[
        str, typer.Option(help="AWS region of the deployed stacks")
    ] = None,
):
    """
    Calls the cdk destroy command.
    """
    confirm = Confirm.ask(f"[#00BCF7]Are you sure?")
    print()

    options = {
        "region": "" if region == "my default" else region,
    }
    options_json = json.dumps(options)

    if confirm:
        ensure_cdk_dependencies()
        run_cdk_command(
            "destroy", "ChunkwiseEcsStack", "--force", "-c", f"options={options_json}"
        )
        run_cdk_command("destroy", "--all", "--force", "-c", f"options={options_json}")
        delete_secret("chunkwise/openai-api-key", region)

        print(f"[green]✅ Stacks successfullly destroyed")

    else:
        print(f"[red]❌ Stack destruction cancelled.")


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
    print(f"[green]✅ Client built!")


@app.command()
def client_start():
    """
    Calls the client start command.
    """
    ensure_npm_dependencies()
    run_client_command("preview")


@app.command()
def client(
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
