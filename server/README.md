# Chunkwise server

## To install dependencies (creates/uses poetry-managed venv)

`poetry install`
To activate the virtual environment use `eval $(poetry env activate)`

## To set the port that the server will run on

Add a environment file using `touch .env`
Include the following key-value pair in it `PORT=8000`
To export the PORT from .env, run `set -a; source .env; set +a` (in the terminal) from your server folder

## To run the server use

`poetry run uvicorn main:app --reload --port $PORT`
