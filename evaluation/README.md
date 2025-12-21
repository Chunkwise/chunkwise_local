# Evaluation service - Sample requests

## GET /health

Health check endpoint for load balancers.

### Health response

```json
{
  "status": "healthy",
  "service": "evaluation"
}
```

## POST /evaluate

Evaluate one or more chunking strategies on a document from S3.

### Evaluate request (with query generation)

```json
{
  "document_id": "sample_document_small",
  "query_generation_config": {
    "num_rounds": 1,
    "queries_per_corpus": 3
  },
  "chunking_configs": [
    {
      "provider": "langchain",
      "chunker_type": "recursive",
      "chunk_size": 300,
      "chunk_overlap": 20
    }
  ]
}
```

### Evaluate response (with query generation)

```json
{
  "embedding_model": "openai.text-embedding-3-large",
  "corpus_id": "sample_document_small",
  "document_s3_key": "documents/sample_document_small.txt",
  "queries_s3_key": "queries/sample_document_small.csv",
  "queries_generated": true,
  "num_queries": 2,
  "chunkers_evaluated": ["langchain recursive"],
  "results": [
    {
      "iou_mean": 0.203,
      "recall_mean": 1.0,
      "precision_mean": 0.203,
      "precision_omega_mean": 0.604
    }
  ]
}
```

### Evaluate request (using existing queries)

```json
{
  "document_id": "sample_document_small",
  "chunking_configs": [
    {
      "provider": "chonkie",
      "chunker_type": "token",
      "chunk_size": 400,
      "chunk_overlap": 20
    }
  ]
}
```

### Evaluate response (using existing queries)

```json
{
  "embedding_model": "openai.text-embedding-3-large",
  "corpus_id": "sample_document_small",
  "document_s3_key": "documents/sample_document_small.txt",
  "queries_s3_key": "queries/sample_document_small.csv",
  "queries_generated": false,
  "num_queries": 2,
  "chunkers_evaluated": ["chonkie token"],
  "results": [
    {
      "iou_mean": 0.191,
      "recall_mean": 1.0,
      "precision_mean": 0.191,
      "precision_omega_mean": 0.321
    }
  ]
}
```
