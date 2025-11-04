# Core

## To install dependencies (creates/uses poetry-managed venv)

poetry install

## To import to a service

- Run `poetry add ../core`
- Run `poetry install`
- Import to your file. Ex. `from chunkwise_core.types import Chunk`

## Packages available to import

- types
  - Chunk
  - RecursiveLevel
  - RecursiveRules
  - BaseChunkerConfig
  - RecursiveChunkerConfig
  - TokenChunkerConfig
  - GeneralChunkerConfig
