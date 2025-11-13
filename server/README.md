# Chunkwise server

## To install dependencies (creates/uses poetry-managed venv)

`poetry install`

To activate the virtual environment use `eval $(poetry env activate)`

## To setup s3

1. Create a bucket on s3 with a name of your choosing such as 'chunkwise_test1'.

2. Create a .env file (under /server) with `S3_BUCKET_NAME=[your s3 bucket name]`.

3. You should already have installed AWS CLI in the CDK Workshop but if you haven't,
   do that then configure your account using `aws configure`

## To run the server use

poetry run uvicorn main:app --reload --port 8000
