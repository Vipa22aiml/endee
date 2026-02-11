# Endee MCP Configuration

## Environment Variables

### Required

- **ENDEE_URL**: URL of the Endee vector database server
  - Default: `http://localhost:8080`
  - Example: `http://endee:8080` (Docker internal)

### Optional

- **ENDEE_AUTH_TOKEN**: Authentication token if Endee has auth enabled
  - Default: (empty - no auth)
  - Set to same value as Endee's NDD_AUTH_TOKEN

### Embedding Configuration

- **EMBEDDING_PROVIDER**: Which embedding provider to use
  - `auto`: Automatically choose (OpenAI if key available, else local)
  - `openai`: Use OpenAI API (requires OPENAI_API_KEY)
  - `local`: Use local sentence-transformers model
  - `none`: Disable embedding generation
  - Default: `auto`

- **OPENAI_API_KEY**: Your OpenAI API key
  - Required if using OpenAI embeddings
  - Get from: https://platform.openai.com/api-keys

- **OPENAI_EMBEDDING_MODEL**: OpenAI embedding model to use
  - Options: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`
  - Default: `text-embedding-3-small`
  - Dimensions: 1536 (small), 3072 (large), 1536 (ada-002)

- **LOCAL_EMBEDDING_MODEL**: HuggingFace model for local embeddings
  - Default: `sentence-transformers/all-MiniLM-L6-v2`
  - Other options: `BAAI/bge-small-en-v1.5`, `sentence-transformers/all-mpnet-base-v2`
  - Dimensions vary by model (384, 768, etc.)

- **PRELOAD_LOCAL_MODEL**: Whether to load local model on startup
  - `true`: Load immediately (faster first request, slower startup)
  - `false`: Load on first use (faster startup, slower first request)
  - Default: `false`

### MCP Server Configuration

- **MCP_TRANSPORT**: Transport protocol for MCP
  - `stdio`: Standard input/output (for CLI tools)
  - `sse`: Server-Sent Events (for remote connections)
  - Default: `stdio`

- **MCP_SSE_PORT**: Port for SSE transport
  - Default: `3000`
  - Only used when MCP_TRANSPORT=sse

## Example Configurations

### Basic Setup (No Auth, Local Embeddings)

```bash
ENDEE_URL=http://localhost:8080
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### With OpenAI Embeddings (BYOK)

```bash
ENDEE_URL=http://localhost:8080
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### With Endee Authentication

```bash
ENDEE_URL=http://localhost:8080
ENDEE_AUTH_TOKEN=your-secret-token
EMBEDDING_PROVIDER=auto
OPENAI_API_KEY=sk-...
```

### Docker Compose Setup

```bash
# Endee Configuration
ENDEE_AUTH_TOKEN=          # Leave empty for no auth
ENDEE_MAX_MEMORY_GB=8

# Embedding Configuration
EMBEDDING_PROVIDER=auto

# OpenAI (BYOK)
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Local Embedding Model
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
PRELOAD_LOCAL_MODEL=false

# MCP Transport
MCP_TRANSPORT=stdio
```

## AI Tool Configuration Examples

### Claude Desktop

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

### OpenCode

```json
{
  "mcp": {
    "endee": {
      "type": "local",
      "command": ["python", "-m", "endee_mcp.server"],
      "environment": {
        "ENDEE_URL": "http://localhost:8080",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

### Cursor

```json
{
  "servers": {
    "endee": {
      "command": "python",
      "args": ["-m", "endee_mcp.server"],
      "env": {
        "ENDEE_URL": "http://localhost:8080"
      }
    }
  }
}
```
