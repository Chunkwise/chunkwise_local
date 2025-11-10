DROP TABLE IF EXISTS workflow;

CREATE TABLE workflow (
  id SERIAL PRIMARY KEY,
  document_id SERIAL UNIQUE NOT NULL,
  chunking_strategy TEXT,
  chunks_stats TEXT,
  visualization_html TEXT,
  evaluation_metrics TEXT
);