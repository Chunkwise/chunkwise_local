# Chunkwise server

## To install dependencies (creates/uses poetry-managed venv)

`poetry install`

To activate the virtual environment use `eval $(poetry env activate)`

## To setup s3

1. Create a bucket on s3 with a name of your choosing such as 'chunkwise_test1'.

2. Create a .env file (under /server) with `S3_BUCKET_NAME=[your s3 bucket name]`.

3. You should already have installed AWS CLI in the CDK Workshop but if you haven't,
   do that then configure your account using `aws configure`

## To connect to the database

After adding things for s3. add these feilds for the Amazon RDS instance.

OPENAI_API_KEY=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

## To run the server use

poetry run uvicorn main:app --reload --port 8000
