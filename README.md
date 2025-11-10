# Chunkwise

To run each server, use these commands:

server:
poetry run uvicorn main:app --reload --port 8000

chunking:
poetry run uvicorn main:app --reload --port 8001

visualization:
poetry run uvicorn main:app --reload --port 8002

evaluation:
poetry run uvicorn main:app --reload --port 8003
