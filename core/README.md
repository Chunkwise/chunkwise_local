# Core

## To install dependencies (creates/uses poetry-managed venv)

poetry install

## To import to a service

- Run `poetry add --editable ../core` (for production remove --editable)
- Run `poetry install`
- Import to your file. Ex. `from chunkwise_core import Chunk`

## Classes available to import

- types
  - Chunk
  - RecursiveLevel
  - RecursiveRules
  - BaseChunkerConfig
  - RecursiveChunkerConfig
  - TokenChunkerConfig
  - GeneralChunkerConfig
