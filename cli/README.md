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
creates a secret, and bootstraps and deploys the AWS stacks.

`typer cli.py run client-run (--region=<NON_DEFAULT_REGION_HERE>)`

Runs both the `client-build` and `client-start` commands.

`typer cli.py run client-build (--region=<NON_DEFAULT_REGION_HERE>)`

Builds the React client. The ALB DNS is retreived automatically,
but if the stack was deployed in a region other than the default,
you must pass in the region as well. Otherwise region can be left
off.

`typer cli.py run client-start`

Runs a built client using Vite. To stop the server use Ctrl^C.

`typer cli.py run destroy (--region=<NON_DEFAULT_REGION_HERE>)`

Destroys AWS resources deployed by the CLI.
Destruction behavior depends on the environment mode (set in `cdk/config.py):

### Development mode

Completely removes all stacks and deletes all secrets:

- All CloudFormation stacks
- Secrets Manager entries (including database credentials and OpenAI API key)
- The S3 bucket
- Both RDS instances

This is a complete teardown.

### Production mode

Only destroys the application-layer stacks:

- ChunkwiseEcsStack
- ChunkwiseLoadBalancerStack
- ChunkwiseBatchStack

Retains:

- ChunkwiseNetworkStack
- ChunkwiseDataStack (including 2 RDS instances and S3 bucket)
- All database credentials and OpenAI API key in Secrets Manager

This prevents accidental loss of persistent production data.

To fully decommission and remove retained production data, see below.

`typer cli.py run destroy-data (--region=<REGION>)`
🔥 Permanently deletes all remaining resources after the regular `destroy`, including the data layer and the network stack (PRODUCTION ONLY)

This command irreversibly deletes:

- ChunkwiseDataStack (including 2 RDS instances and the S3 bucket)
- Database credentials and OpenAI API key secrets
- Any retained data in ChunkwiseDataStack
- ChunkwiseNetworkStack

What it does not delete:

- ChunkwiseEcsStack
- ChunkwiseLoadBalancerStack
- ChunkwiseBatchStack

How it works:
`destroy-data` internally:

- Re-deploys ChunkwiseDataStack with `allow_rds_delete=true`
- Disables deletion protection on both RDS instances
- Destroys ChunkwiseDataStack
- Deletes chunkwise/db-credentials and chunkwise/production-db-credentials
- Destroys ChunkwiseNetworkStack

You will be required to type `DELETE DATA` to confirm.

## Fully removing production resources manually

If you want to completely remove all retained production resources without using the CLI, use the following commands and make sure to pass `--region` if not using the default one:

Delete the OpenAI API key:

```bash
aws secretsmanager delete-secret \
 --secret-id chunkwise/openai-api-key \
 --force-delete-without-recovery \
 --region <YOUR_REGION>
```

Delete database credentials:

```bash
aws secretsmanager delete-secret \
 --secret-id chunkwise/db-credentials \
 --force-delete-without-recovery \
 --region <YOUR_REGION>

 aws secretsmanager delete-secret \
 --secret-id chunkwise/production-db-credentials \
 --force-delete-without-recovery \
 --region <YOUR_REGION>
```

Delete the S3 bucket:

```bash
aws s3 rm s3://chunkwise-<ACCOUNT_ID> --recursive --region <YOUR_REGION>
aws s3api delete-bucket --bucket chunkwise-<ACCOUNT_ID> --region <YOUR_REGION>
```

Delete remaining stacks:

```bash
cdk destroy ChunkwiseDataStack --force -c options='{"region":"<YOUR_REGION>"}'
cdk destroy ChunkwiseNetworkStack --force -c options='{"region":"<YOUR_REGION>"}'
```
