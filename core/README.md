# Core

## To install dependencies (creates/uses poetry-managed venv)

poetry install

## To import to a service

- Run `poetry add --editable ../core` (for production remove --editable)
- Run `poetry install`
- Import to your file. Ex. `from chunkwise_core import Chunk`

## To test the Chonkie Semantic and Chonkie Slumber chunkers you need an OpenAI API key

- generate an OPENAI API key

- create a .env file with:

  `OPENAI_API_KEY=[your_api_key]`

## Classes available to import

- types
  - Chunk
  - RecursiveLevel
  - RecursiveRules
  - BaseChunkerConfig
  - RecursiveChunkerConfig
  - TokenChunkerConfig
  - GeneralChunkerConfig
