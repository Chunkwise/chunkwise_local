# COMMAND LINE INTERFACE

## How to use:

This folder contains the command line interface provided by a
library called Typer. To use it, first run `poetry install`.
Next activate the virtual environment with
`eval $(poetry env activate)`.

Once you've done that the below commands are available to you.

## COMMANDS

`typer cli.py run deploy`

Initiates a user interface that gathers the necessary information
to deploy an AWS stack, then triggers the deployment.

`typer cli.py run destroy`

Forcefully deletes all of the AWS stacks created by deploy. Note
that this doesn't destroy the S3 bucket, RDS instances, or
the created secrets.

`typer cli.py run client`

Runs both the `client-build` and `client-start` commands.

`typer cli.py run client-build <YOUR_ALB_DNS_HERE>`

Builds the React client.

`typer cli.py run client-start <YOUR_ALB_DNS_HERE>`

Runs a built client using Vite. To stop the server use Ctrl^C.

# If you would like to destroy the created secret immediately use this command:

`aws secretsmanager delete-secret --secret-id chunkwise/openai-api-key --force-delete-without-recovery --region <YOUR_REGION_HERE>`
