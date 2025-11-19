DROP TABLE IF EXISTS workflow_1;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE workflow_1 (
  id SERIAL PRIMARY KEY,
  document_key TEXT NOT NULL,
  chunk_id INT NOT NULL,
  chunk_text TEXT NOT NULL,
  embedding VECTOR(1536) NOT NULL
);
