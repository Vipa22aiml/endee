# Endee MCP Framework

MCP (Model Context Protocol) server for Endee Vector Database. Enables AI tools like Claude Code, OpenCode, and Cursor to interact with Endee's vector search capabilities.

## Features

- **20 MCP Tools**: Complete coverage of Endee functionality
- **Dual Embedding Support**: BYOK (OpenAI) + Local (sentence-transformers)
- **Easy Deployment**: Docker Compose with Endee + MCP services
- **Multiple Transports**: stdio (primary) + SSE (optional)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/EndeeLabs/endee.git
cd endee
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Configure Your AI Tool

#### Claude Desktop
```json
{
  "mcpServers": {
    "endee": {
      "command": "docker",
      "args": ["exec", "-i", "endee-mcp", "python", "-m", "endee_mcp.server"]
    }
  }
}
```

#### OpenCode
```json
{
  "mcp": {
    "endee": {
      "type": "local",
      "command": ["python", "-m", "endee_mcp.server"],
      "environment": {
        "ENDEE_URL": "http://localhost:8080"
      }
    }
  }
}
```

## Available Tools

### Index Management
- `endee_create_index` - Create new vector index
- `endee_list_indexes` - List all indexes
- `endee_describe_index` - Get index details
- `endee_delete_index` - Delete index

### Vector Operations
- `endee_upsert_vectors` - Insert with pre-computed embeddings
- `endee_upsert_documents` - Insert with auto-embedding
- `endee_get_vector` - Retrieve by ID
- `endee_delete_vector` - Delete by ID
- `endee_delete_by_filter` - Bulk delete

### Search
- `endee_search` - Vector-based search
- `endee_search_text` - Text query with auto-embedding
- `endee_hybrid_search` - Dense + sparse search

### Batch Import
- `endee_import_json` - Import from JSON/JSONL
- `endee_import_csv` - Import from CSV

### Backup
- `endee_create_backup` - Create backup
- `endee_list_backups` - List backups
- `endee_restore_backup` - Restore from backup
- `endee_delete_backup` - Delete backup

### System
- `endee_health_check` - Server health
- `endee_get_config` - Configuration info

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENDEE_URL` | Yes | `http://localhost:8080` | Endee server URL |
| `ENDEE_AUTH_TOKEN` | No | - | Auth token |
| `EMBEDDING_PROVIDER` | No | `auto` | `auto`/`openai`/`local`/`none` |
| `OPENAI_API_KEY` | If using OpenAI | - | OpenAI API key |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | OpenAI model |
| `LOCAL_EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | Local model |
| `MCP_TRANSPORT` | No | `stdio` | `stdio` or `sse` |

## License

Apache License 2.0
