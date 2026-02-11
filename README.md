# Endee MCP Framework

MCP (Model Context Protocol) server for Endee Vector Database. This fork focuses on the MCP integration so AI tools like Claude Code, OpenCode, and Cursor can access Endee search workflows.

<!-- Screenshot: Endee MCP in Claude Code -->

## Quick Start

```bash
# Clone this fork
git clone https://github.com/Vipa22aiml/endee_mcp.git
cd endee_mcp/endee_mcp

# Copy environment configuration
cp .env.example .env

# Start services
docker-compose up -d

# Configure your AI tool (see below)
```

## Features

- **21 MCP Tools**: Complete coverage of Endee functionality
- **Dual Embedding Support**: BYOK (OpenAI) + Local (sentence-transformers)
- **Easy Deployment**: Docker Compose with Endee + MCP services
- **Multiple Transports**: stdio (primary) + SSE (optional)

## MCP Tools

### Index Management

- `endee_create_index`
- `endee_list_indexes`
- `endee_describe_index`
- `endee_delete_index`

### Vector Operations

- `endee_upsert_vectors`
- `endee_upsert_documents`
- `endee_get_vector`
- `endee_delete_vector`
- `endee_delete_by_filter`
- `endee_update_filters`

### Search

- `endee_search`
- `endee_search_text`
- `endee_hybrid_search`

### Batch Import

- `endee_import_json`
- `endee_import_csv`

### Backup

- `endee_create_backup`
- `endee_list_backups`
- `endee_restore_backup`
- `endee_delete_backup`

### System

- `endee_health_check`
- `endee_get_config`

## Documentation

- `endee_mcp/TODO.md` - Implementation status and task list
- `endee_mcp/CONFIGURATION.md` - Environment variables and setup
- `endee_mcp/TOOLS.md` - Complete tool reference
- `endee_mcp/mcp/README.md` - MCP server documentation

## AI Tool Configuration

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
        "ENDEE_URL": "http://localhost:8080"
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

## Project Structure

```
endee_mcp/
├── endee/              # Endee vector database (cloned)
├── mcp/                # MCP server package
│   ├── src/endee_mcp/  # Source code
│   ├── pyproject.toml  # Python dependencies
│   └── Dockerfile      # Container build
├── docker-compose.yml  # Docker orchestration
├── .env.example        # Configuration template
├── TODO.md            # Implementation tasks
├── CONFIGURATION.md   # Setup guide
└── TOOLS.md           # Tool reference
```

## License

Apache License 2.0
