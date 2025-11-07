# Chunking Evaluation Service

## To install dependencies

`poetry install`

## To run the server

`poetry run uvicorn main:app --reload [--PORT_NUM]`

- server runs on port 8000 by default

## To test the evaluation function locally or use the /evaluate endpoint:

- generate an OPENAI API key (for calling the embedding model & query generation via LLM)

- create a .env file with:

  `OPENAI_API_KEY=[your_api_key]`

## To run the server

`poetry run uvicorn main:app --reload`

## For MVP local testing

- The evaluate endpoint accepts the document content as a string (instead of a document path for production)
- A .txt file (with a title in the format of "temp*doc*[random string]") will be created, which contains the passed string
- The .txt file will be saved in the designated directory (/data by default), where the LLM-generated queries CSV file will also be stored