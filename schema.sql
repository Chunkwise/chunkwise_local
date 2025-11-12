DROP TABLE IF EXISTS workflow;

CREATE TABLE workflow (
  id SERIAL PRIMARY KEY,
  title varchar(50) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT NOW(),
  document_title TEXT,
  chunking_strategy TEXT,
  chunks_stats TEXT,
  visualization_html TEXT,
  evaluation_metrics TEXT
);