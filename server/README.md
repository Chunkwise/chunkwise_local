# Chunkwise server

## To install dependencies (creates/uses poetry-managed venv)

`poetry install`

To activate the virtual environment use `eval $(poetry env activate)`

## To run the server use

poetry run uvicorn main:app --reload --port 8000
