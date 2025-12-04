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
to deploy the stacks. It then installs necessary dependencies,
creates a secret, and bootstraps and deploys the stacks.

`typer cli.py run destroy --region=<NON_DEFAULT_REGION_HERE>`

Forcefully deletes all of the AWS stacks created by deploy. Note
that this doesn't destroy the S3 bucket, RDS instances, or
the created secrets. Also, if you used a non-default region
make sure to specify that here.

`typer cli.py run client --region=<NON_DEFAULT_REGION_HERE>`

Runs both the `client-build` and `client-start` commands.

`typer cli.py run client-build --region=<NON_DEFAULT_REGION_HERE>`

Builds the React client. The ALB DNS is retreived automatically,
but if the stack was deployed in a region other than the default,
you must pass in the region as well. Otherwise region can be left
off.

`typer cli.py run client-start`

Runs a built client using Vite. To stop the server use Ctrl^C.

# If you would like to destroy the created secret immediately use this command:

`aws secretsmanager delete-secret --secret-id chunkwise/openai-api-key --force-delete-without-recovery --region <YOUR_REGION_HERE>`
