FROM python:3.13

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY process_document.py .
COPY config.py .
COPY services.py .
COPY utils.py .

CMD ["python", "process_document.py"]

