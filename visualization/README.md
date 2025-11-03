# Visualization

## To clone

git clone [repo link]
cd repo

## To install dependencies (creates/uses poetry-managed venv)

cd visualization
poetry install

## To run the server

poetry run uvicorn main:app --reload --port 8002
