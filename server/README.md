# Server - Sample requests

## GET /api/health

Health check endpoint.

### Health response

```json
{
  "status": "ok"
}
```

## GET /api/configs

Returns adjustable parameters for each chunker's config.

### Configs response

```json
{
  "chonkie": {
    "token": ["chunk_size", "chunk_overlap"],
    "sentence": ["chunk_size", "chunk_overlap", "min_sentences_per_chunk"],
    "semantic": ["chunk_size", "chunk_overlap", "min_sentences_per_chunk"]
  },
  "langchain": {
    "recursive": ["chunk_size", "chunk_overlap"],
    "character": ["chunk_size", "chunk_overlap"]
  }
}
```

## GET /api/documents

Returns a list of all document IDs in S3.

### Documents list response

```json
["document_one", "document_two", "document_three"]
```

## POST /api/documents

Uploads a document to S3.

### Document upload request

```json
{
  "document_title": "The Princess and the Pea",
  "document_content": "Once upon a time there was a prince who wanted to marry a princess..."
}
```

### Document upload response

```json
{
  "detail": "Successfully uploaded The Princess and the Pea"
}
```

## DELETE /api/documents/{document_title}

Deletes a document from S3.

### Document delete response

```json
{
  "detail": "deleted"
}
```

## GET /api/workflows

Returns a list of all workflows.

### Workflows list response

```json
[
  {
    "id": 1,
    "title": "Workflow1",
    "document_title": null,
    "chunking_strategy": null,
    "evaluation_metrics": null,
    "visualization_html": null,
    "chunks_stats": null
  }
]
```

## POST /api/workflows

Creates a new workflow.

### Workflow create request

```json
{
  "title": "Workflow1"
}
```

### Workflow create response

```json
{
  "id": 1,
  "title": "Workflow1"
}
```

## PUT /api/workflows/{workflow_id}

Updates a workflow. Can include any combination of properties.

### Workflow update request

```json
{
  "document_title": "The Princess and the Pea",
  "chunking_strategy": {
    "chunk_size": 120,
    "chunk_overlap": 20,
    "provider": "chonkie",
    "chunker_type": "token"
  }
}
```

### Workflow update response

```json
{
  "id": 1,
  "title": "Workflow1",
  "document_title": "The Princess and the Pea",
  "chunking_strategy": {
    "chunk_size": 120,
    "chunk_overlap": 20,
    "provider": "chonkie",
    "chunker_type": "token"
  }
}
```

## DELETE /api/workflows/{workflow_id}

Deletes a workflow.

### Workflow delete response

```json
{
  "detail": "successfully deleted workflow."
}
```

## GET /api/workflows/{workflow_id}/visualization

Generates visualization for a workflow's chunks.

### Visualization response

```json
{
  "stats": {
    "total_chunks": 543,
    "largest_chunk_chars": 213,
    "largest_text": "example largest",
    "smallest_chunk_chars": 21,
    "smallest_text": "example smallest",
    "avg_chars": 117.5
  },
  "html": "<div class='chunk'>...</div>"
}
```

## GET /api/workflows/{workflow_id}/evaluation

Evaluates chunking strategy for a workflow.

### Evaluation response

```json
{
  "embedding_model": "text-embedding-3-small",
  "corpus_id": "document_title",
  "document_s3_key": "documents/document_title.txt",
  "queries_s3_key": "queries/document_title.csv",
  "queries_generated": true,
  "num_queries": 5,
  "chunkers_evaluated": ["chonkie token"],
  "results": [
    {
      "iou_mean": 0.15,
      "recall_mean": 0.85,
      "precision_mean": 0.12,
      "precision_omega_mean": 0.35
    }
  ]
}
```

## POST /api/ephemeral-key

Creates an ephemeral RSA key pair for encrypting sensitive data.

### Ephemeral key response

```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
  "expires_in": 60
}
```

## POST /api/workflows/{workflow_id}/deploy

Deploys a workflow to process documents from user's S3 bucket. Returns Server-Sent Events (SSE).

### Deploy request

```json
{
  "crypto_token": "550e8400-e29b-41d4-a716-446655440000",
  "encrypted_credentials_b64": "base64_encrypted_s3_credentials",
  "s3_bucket": "my-documents-bucket"
}
```
