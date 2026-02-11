# Endee MCP Tools Reference

Complete reference for all 21 MCP tools.

## Index Management

### endee_create_index

Create a new vector index.

**Parameters:**
- `name` (string, required): Unique name for the index
- `dimension` (integer, required): Vector dimensionality (2-16384)
- `space_type` (string, optional): Distance metric - "cosine", "l2", or "ip". Default: "cosine"
- `precision` (string, optional): Quantization - "binary", "int8d", "int16d", "float16", "float32". Default: "int8d"
- `sparse_dimension` (integer, optional): For hybrid search. Enable if > 0
- `m` (integer, optional): HNSW connectivity (4-512). Default: 16
- `ef_construction` (integer, optional): Build quality (8-4096). Default: 128

**Returns:** Success message

**Example:**
```json
{
  "name": "documents",
  "dimension": 1536,
  "space_type": "cosine",
  "precision": "int8d"
}
```

### endee_list_indexes

List all available indexes.

**Parameters:** None

**Returns:** Array of index objects with metadata

### endee_describe_index

Get detailed information about an index.

**Parameters:**
- `name` (string, required): Index name

**Returns:** Index details (dimension, space_type, total_elements, etc.)

### endee_delete_index

Delete an index and all its data.

**Parameters:**
- `name` (string, required): Index name
- `confirm` (boolean, required): Must be true to confirm

**Returns:** Success message

## Vector Operations

### endee_upsert_vectors

Insert or update vectors with pre-computed embeddings.

**Parameters:**
- `index_name` (string, required): Target index
- `vectors` (array, required): List of vector objects
  - `id` (string): Unique identifier
  - `vector` (array of floats): Embedding vector
  - `meta` (object, optional): Metadata
  - `filter` (object, optional): Filterable fields
  - `sparse_indices` (array, optional): For hybrid search
  - `sparse_values` (array, optional): For hybrid search

**Returns:** Upserted count

**Example:**
```json
{
  "index_name": "documents",
  "vectors": [
    {
      "id": "doc_001",
      "vector": [0.1, 0.2, ...],
      "meta": {"title": "Hello"},
      "filter": {"category": "tech"}
    }
  ]
}
```

### endee_upsert_documents

Insert documents with automatic embedding generation.

**Parameters:**
- `index_name` (string, required): Target index
- `documents` (array, required): List of documents
  - `id` (string): Unique identifier
  - `text` (string): Content to embed
  - `meta` (object, optional): Metadata
  - `filter` (object, optional): Filterable fields
- `embedding_provider` (string, optional): "openai", "local", or "auto"
- `embedding_model` (string, optional): Override default model

**Returns:** Upserted count, tokens used, provider info

**Example:**
```json
{
  "index_name": "knowledge_base",
  "documents": [
    {
      "id": "faq_001",
      "text": "How do I reset my password?",
      "meta": {"source": "faq"},
      "filter": {"category": "account"}
    }
  ],
  "embedding_provider": "openai"
}
```

### endee_get_vector

Retrieve a vector by ID.

**Parameters:**
- `index_name` (string, required): Index name
- `vector_id` (string, required): Vector ID
- `include_vector` (boolean, optional): Include raw vector data

**Returns:** Vector info with optional raw vector

### endee_delete_vector

Delete a vector by ID.

**Parameters:**
- `index_name` (string, required): Index name
- `vector_id` (string, required): Vector ID

**Returns:** Success message

### endee_delete_by_filter

Delete vectors matching filter criteria.

**Parameters:**
- `index_name` (string, required): Index name
- `filter` (array, required): Filter conditions
  - `$eq`: Exact match `{"field": {"$eq": "value"}}`
  - `$in`: Match any `{"field": {"$in": ["a", "b"]}}`
  - `$range`: Numeric range `{"field": {"$range": [min, max]}}`

**Returns:** Deleted count

**Example:**
```json
{
  "index_name": "documents",
  "filter": [
    {"category": {"$eq": "outdated"}}
  ]
}
```

### endee_update_filters

Update filter fields for existing vectors.

**Parameters:**
- `index_name` (string, required): Name of the index
- `updates` (array, required): List of update objects
  - `id` (string): Vector ID to update
  - `filter` (object): New filter fields

**Returns:** Updated count

**Example:**
```json
{
  "index_name": "documents",
  "updates": [
    {"id": "doc1", "filter": {"category": "updated", "status": "active"}},
    {"id": "doc2", "filter": {"category": "updated", "status": "pending"}}
  ]
}
```

## Search

### endee_search

Search with pre-computed query vector.

**Parameters:**
- `index_name` (string, required): Index to search
- `vector` (array of floats, required): Query vector
- `top_k` (integer, optional): Number of results (1-4096). Default: 10
- `filter` (array, optional): Filter conditions
- `ef` (integer, optional): Search quality (higher = better). Default: 128
- `include_vectors` (boolean, optional): Include vector data

**Returns:** Search results with similarity scores

### endee_search_text

Search with text query (auto-embedding).

**Parameters:**
- `index_name` (string, required): Index to search
- `query` (string, required): Search query text
- `top_k` (integer, optional): Number of results. Default: 10
- `filter` (array, optional): Filter conditions
- `ef` (integer, optional): Search quality. Default: 128
- `embedding_provider` (string, optional): "openai", "local", or "auto"
- `embedding_model` (string, optional): Override model

**Returns:** Search results with provider info

**Example:**
```json
{
  "index_name": "knowledge_base",
  "query": "How do I reset my password?",
  "top_k": 5,
  "filter": [
    {"category": {"$eq": "account"}}
  ]
}
```

### endee_hybrid_search

Combined dense + sparse search.

**Parameters:**
- `index_name` (string, required): Hybrid index name
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of results. Default: 10
- `filter` (array, optional): Filter conditions
- `dense_weight` (float, optional): Weight for dense (0.0-1.0). Default: 0.7
- `embedding_provider` (string, optional): Provider for dense vectors

**Returns:** Hybrid search results

## Batch Import

### endee_import_json

Import from JSON or JSONL file.

**Parameters:**
- `index_name` (string, required): Target index
- `file_path` (string, required): Path to file
- `id_field` (string, optional): Field for ID. Default: "id"
- `text_field` (string, optional): Field with text to embed
- `vector_field` (string, optional): Field with pre-computed vectors
- `meta_fields` (array, optional): Fields for metadata
- `filter_fields` (array, optional): Fields for filtering
- `batch_size` (integer, optional): Records per batch. Default: 100
- `embedding_provider` (string, optional): Provider

**Returns:** Import statistics

### endee_import_csv

Import from CSV file.

**Parameters:**
- `index_name` (string, required): Target index
- `file_path` (string, required): Path to CSV
- `id_column` (string, optional): Column for ID. Default: "id"
- `text_column` (string, optional): Column with text
- `vector_column` (string, optional): Column with vectors
- `meta_columns` (array, optional): Columns for metadata
- `filter_columns` (array, optional): Columns for filtering
- `delimiter` (string, optional): CSV delimiter. Default: ","
- `batch_size` (integer, optional): Records per batch. Default: 100
- `embedding_provider` (string, optional): Provider

**Returns:** Import statistics

## Backup

### endee_create_backup

Create backup of index.

**Parameters:**
- `index_name` (string, required): Index to backup
- `backup_name` (string, required): Name for backup

**Returns:** Success message

### endee_list_backups

List available backups.

**Parameters:** None

**Returns:** List of backup names

### endee_restore_backup

Restore from backup.

**Parameters:**
- `backup_name` (string, required): Backup to restore
- `target_index_name` (string, required): New index name (must not exist)

**Returns:** Success message

### endee_delete_backup

Delete a backup.

**Parameters:**
- `backup_name` (string, required): Backup name
- `confirm` (boolean, required): Must be true

**Returns:** Success message

## System

### endee_health_check

Check server health.

**Parameters:** None

**Returns:** Health status, Endee URL, embedding provider info

### endee_get_config

Get configuration info.

**Parameters:** None

**Returns:** Current configuration (sanitized)
