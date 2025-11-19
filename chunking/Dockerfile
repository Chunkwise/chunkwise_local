FROM python:3.13

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY get_chunks_with_metadata.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
