# Chunking service - Sample requests

## GET /health

Health check endpoint for load balancers.

### Health response

```json
{
  "status": "healthy",
  "service": "chunking"
}
```

## POST /chunk

Chunk text and return an array of strings.

### Chunk request

```json
{
  "chunker_config": {
    "chunker_type": "token",
    "provider": "chonkie",
    "chunk_size": 500,
    "chunk_overlap": 50
  },
  "text": "Your text content here..."
}
```

### Chunk response

```json
["First chunk of text...", "Second chunk of text...", "Third chunk of text..."]
```

## POST /chunk_with_metadata

Chunk text and return an array of chunks with metadata.

### Chunk with metadata request

```json
{
  "chunker_config": {
    "chunker_type": "token",
    "provider": "chonkie",
    "chunk_size": 500,
    "chunk_overlap": 50
  },
  "text": "Your text content here..."
}
```

### Chunk with metadata response

```json
[
  {
    "text": "First chunk of text...",
    "start_index": 0,
    "end_index": 500,
    "token_count": 500
  },
  {
    "text": "Second chunk of text...",
    "start_index": 450,
    "end_index": 950,
    "token_count": 500
  }
]
```
