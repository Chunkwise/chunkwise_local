# Chunkwise server

## To install dependencies (creates/uses poetry-managed venv)

`poetry install`

To activate the virtual environment use `eval $(poetry env activate)`

## To setup s3

1. Create a bucket on s3 with a name of your choosing such as 'chunkwise_test1'.

2. Set the var `BUCKET_NAME` to be the same as what you just created on s3.

3. You should already have installed AWS CLI in the CDK Workshop but if you haven't,
   do that then configure your account using `aws configure`

## To run the server use

poetry run uvicorn main:app --reload --port 8000
