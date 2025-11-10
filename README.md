# Chunkwise

## In order to use this, you will need to have installed:

- PostgreSQL
- Python
  - Poetry
- Node & NPM

## To initialize the database:

From the projects root directory use these commands:

1. createdb chunkwise
2. psql chunkwise < schema.sql

## To run each server:

From each server's root directory use these commands:

server:
poetry run uvicorn main:app --reload --port 8000

chunking:
poetry run uvicorn main:app --reload --port 8001

visualization:
poetry run uvicorn main:app --reload --port 8002

evaluation:
poetry run uvicorn main:app --reload --port 8003

client:
npm run dev
