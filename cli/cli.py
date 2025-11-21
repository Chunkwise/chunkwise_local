import os
import json
import subprocess
from pathlib import Path
import typer
from rich import print
from rich.pretty import pprint
from rich.prompt import Prompt, Confirm, InvalidResponse

# aws secretsmanager create-secret --name chunkwise/openai-api-key --secret-string aklsdjlkasjdlkjsa
# aws secretsmanager delete-secret --secret-id chunkwise/openai-api-key --force-delete-without-recovery --region us-east-1

app = typer.Typer()

CDK_DIR = Path(__file__).resolve().parent.parent / "cdk"


def validate_key(key):
    if not isinstance(key, str) or len(key) == 0:
        raise InvalidResponse("Please enter a string with characters")


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
        typer.echo("📦 Ensuring CDK dependencies with pip...")
        cmd = ["pip", "install", "-r", "requirements.txt"]
    else:
        typer.echo("⚠️ No dependency file found in CDK directory.")
        return

    # Install inside the CDK directory
    proc = subprocess.Popen(
        cmd,
        cwd=CDK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    for line in proc.stdout:
        typer.echo(line.rstrip())

    proc.wait()

    if proc.returncode != 0:
        typer.echo("❌ CDK dependency installation failed.")
        raise typer.Exit(code=1)

    typer.echo("✅ CDK dependencies ready!")


def run_cdk_command(*args):
    """
    Runs a CDK command inside the CDK directory.
    Streams output live and preserves exit codes.
    """

    ensure_cdk_dependencies()

    typer.echo(f"👉 Running: cdk {' '.join(args)} (in {CDK_DIR})")

    try:
        proc = subprocess.Popen(
            ["cdk"] + list(args),
            cwd=CDK_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Stream output line-by-line
        for line in proc.stdout:
            typer.echo(line.rstrip())

        proc.wait()

        if proc.returncode != 0:
            raise typer.Exit(code=proc.returncode)

        typer.echo("✅ Stacks deployed!")

    except FileNotFoundError:
        typer.echo("❌ Error: CDK is not installed or not in PATH.")
        raise typer.Exit(code=1)


def create_secret(secret_name, secret_value):
    """
    Runs a AWS CLI command inside to create a secret.
    """

    typer.echo(
        f"👉 Running: aws secretsmanager create-secret --name {secret_name} --secret-string *******"
    )

    try:
        proc = subprocess.Popen(
            [
                "aws",
                "secretsmanager",
                "create-secret",
                "--name",
                secret_name,
                "--secret-string",
                secret_value,
            ],
            cwd=CDK_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Stream output line-by-line
        for line in proc.stdout:
            typer.echo(line.rstrip())

        proc.wait()

        if proc.returncode != 0:
            raise typer.Exit(code=proc.returncode)

        typer.echo("✅ AWS Secret created!")

    except FileNotFoundError:
        typer.echo("❌ Error: CLI is not installed or not in PATH.")
        raise typer.Exit(code=1)


@app.command()
def deploy():
    """
    This command displays the beautiful Chunkwise logo, then it
    gathers some information from the user which it puts into a
    JSON string to send to the AWS CDK. Finally it will trigger
    the `cdk deploy` command.
    """
    display_logo()

    openai_api_key = Prompt.ask(
        f"[#00BCF7]OpenAI Api key", password=False
    )  # Could make password True to hide while typing
    print()
    validate_key(openai_api_key)

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
    )
    print()

    confirm = Confirm.ask(f"[#00BCF7]Are you sure?")
    print()

    if confirm:
        options = {
            "region": "" if region == "my default" else region,
        }
        options_json = json.dumps(options)

        create_secret("chunkwise/openai-api-key", openai_api_key)
        run_cdk_command(
            "deploy",
            "--all",
            "--require-approval",
            "never",
            "-c",
            f"options={options_json}",
        )
    else:
        print(f"[red]Deployment cancelled")


@app.command()
def destroy():
    """
    Calls the cdk destroy command.
    """
    run_cdk_command("destroy", "ChunkwiseEcsStack", "--force")
    run_cdk_command("destroy", "ChunkwiseLoadBalancerStack", "--force")
    run_cdk_command("destroy", "ChunkwiseDatabaseStack", "--force")
    run_cdk_command("destroy", "ChunkwiseNetworkStack", "--force")


@app.command()
def client_build():
    """
    Calls the client build command.
    """
    print("building the client...")
    print("client built")


@app.command()
def client_start():
    """
    Calls the client start command.
    """
    print("starting the client...")
    print("client running")


@app.command()
def client():
    """
    Calls the client build then client start commands
    in squence.
    """
    client_build()
    client_start()
