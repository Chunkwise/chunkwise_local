# Chunking

## To install dependencies (creates/uses poetry-managed venv)

poetry install

## To run the server

poetry run uvicorn main:app --reload --port 8001

## Add environment variable

- create a .env file with:

  `OPENAI_API_KEY=[your_api_key]`
