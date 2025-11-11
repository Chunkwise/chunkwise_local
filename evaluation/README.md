# Chunking Evaluation Service

## To install dependencies

`poetry install`

## To run the server

`poetry run uvicorn main:app --reload [--PORT_NUM]`

- server runs on port 8000 by default

## To use the evaluation service with S3 integration:

- generate an OPENAI API key (for calling the embedding model & query generation via LLM)

- configure AWS credentials using CLI or Console

  - if using CLI, boto3 can implicitly loads set credentials
  - if using Console, create an .env with containing `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

- create an S3 bucket on AWS, take note of the bucket name

- create a .env file with:

  `OPENAI_API_KEY=[your_api_key]`
  `S3_BUCKET_NAME=[your_bucket_name]`

## For S3-based MVP testing

- The evaluate endpoint expects from the backend the `document_id`, i.e. the identifier of an S3 document to evaluate
  - e.g. the `document_id` of file `test_document123.txt` is `test_document123`
- The uploaded file for evaluation is expected to have the s3 key in this format:
  `documents/{document_id}.txt`, e.g. `documents/test_document123.txt`
- The generated queries CSV file will have s3 key in this format:
  `queries/{document_id}/llm_queries_{document_id}.csv`, e.g. `queries/test_document123/llm_queries_test_document123.csv`
