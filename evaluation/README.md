# Chunking Evaluation Service

## To install dependencies

`poetry install`

## To run the server

`poetry run uvicorn main:app --reload [--PORT_NUM]`

- server runs on port 8000 by default

## To test the evaluation function locally or use the /evaluate endpoint:

- generate an OPENAI API key (for calling the embedding model)

- create a .env file with:

  `OPENAI_API_KEY=[your_api_key]`
