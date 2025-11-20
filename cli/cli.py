import typer
from rich import print

app = typer.Typer()


def display_logo():
    pass


@app.command()
def deploy(openai_api_key: str, region: str = "us-east-1a", confirm: bool = True):
    if confirm:
        print(f"creating VPC in {region}...")
        print(f"creating secret {openai_api_key}...")
        print("AWS Stack deployed")
    else:
        print("deployment cancelled")


@app.command()
def destroy(include_rds: bool = False):
    print("AWS Stack destroyed")

    if include_rds:
        print("RDS instance destroyed")


@app.command()
def client_build():
    print("building the client...")
    print("client built")


@app.command()
def client_start():
    print("starting the client...")
    print("client running")


@app.command()
def client():
    client_build()
    client_start()
