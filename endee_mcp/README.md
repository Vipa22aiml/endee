# Endee MCP Framework

MCP (Model Context Protocol) server for Endee Vector Database - enables AI tools like Claude Code, OpenCode, and Cursor to interact with Endee's vector search capabilities.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/EndeeLabs/endee.git
cd endee

# Copy environment configuration
cp .env.example .env

# Start services
docker-compose up -d

# Configure your AI tool (see below)
```

## Features

- **20 MCP Tools**: Complete coverage of Endee functionality
- **Dual Embedding Support**: BYOK (OpenAI) + Local (sentence-transformers)
- **Easy Deployment**: Docker Compose with Endee + MCP services
- **Multiple Transports**: stdio (primary) + SSE (optional)

## Documentation

- [TODO.md](TODO.md) - Implementation status and task list
- [CONFIGURATION.md](CONFIGURATION.md) - Environment variables and setup
- [TOOLS.md](TOOLS.md) - Complete tool reference
- [mcp/README.md](mcp/README.md) - MCP server documentation

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
