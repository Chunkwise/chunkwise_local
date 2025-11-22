DROP TABLE IF EXISTS deployment;

DROP TABLE IF EXISTS chunk;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE deployment (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  created_at timestamptz NOT NULL DEFAULT NOW(),
  chunker_config TEXT NOT NULL,
  deployment_status TEXT
);

CREATE TABLE chunk (
  id SERIAL PRIMARY KEY,
  deployment_id INT REFERENCES deployment(id),
  document_key TEXT NOT NULL,
  chunk_id INT NOT NULL,
  chunk_text TEXT NOT NULL,
  embedding VECTOR(1536) NOT NULL
);
