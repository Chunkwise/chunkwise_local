import os
import json
import typer
from rich import print
from rich.pretty import pprint
from rich.prompt import Prompt, Confirm, InvalidResponse

app = typer.Typer()


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
        ],
        show_choices=False,
        default="us-east-1",
    )
    print()

    confirm = Confirm.ask(f"[#00BCF7]Are you sure?")
    print()

    if confirm:
        options = {
            "openai_api_key": openai_api_key,
            "region": region,
        }
        options_json = json.dumps(options)

        print(f"[green]Deploying stack with options:")
        pprint(options, expand_all=True)
    else:
        print(f"[red]Deployment cancelled")


@app.command()
def destroy():
    """
    Calls the cdk destroy command.
    """
    print("AWS Stack destroyed")


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
