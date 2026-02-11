"""Endee MCP Framework - Configuration management."""

import os
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Config:
    """Configuration for Endee MCP server."""
    
    # Endee connection
    endee_url: str = field(default="http://localhost:8080")
    endee_auth_token: str = field(default="")
    
    # Embedding configuration
    embedding_provider: Literal["auto", "openai", "local", "none"] = field(default="auto")
    
    # OpenAI settings
    openai_api_key: str = field(default="")
    openai_embedding_model: str = field(default="text-embedding-3-small")
    
    # Local embedding settings
    local_embedding_model: str = field(default="sentence-transformers/all-MiniLM-L6-v2")
    preload_local_model: bool = field(default=False)
    
    # MCP transport
    mcp_transport: Literal["stdio", "sse"] = field(default="stdio")
    mcp_sse_port: int = field(default=3000)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            endee_url=os.getenv("ENDEE_URL", "http://localhost:8080"),
            endee_auth_token=os.getenv("ENDEE_AUTH_TOKEN", ""),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "auto"),  # type: ignore
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            local_embedding_model=os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            preload_local_model=os.getenv("PRELOAD_LOCAL_MODEL", "false").lower() == "true",
            mcp_transport=os.getenv("MCP_TRANSPORT", "stdio"),  # type: ignore
            mcp_sse_port=int(os.getenv("MCP_SSE_PORT", "3000")),
        )
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key)
    
    def is_auth_enabled(self) -> bool:
        """Check if Endee authentication is enabled."""
        return bool(self.endee_auth_token)
    
    def get_embedding_provider(self) -> Literal["openai", "local", "none"]:
        """Get the actual embedding provider to use."""
        if self.embedding_provider == "auto":
            if self.is_openai_configured():
                return "openai"
            else:
                return "local"
        return self.embedding_provider  # type: ignore
    
    def to_dict(self) -> dict:
        """Convert config to dictionary (for display)."""
        return {
            "endee_url": self.endee_url,
            "endee_auth_enabled": self.is_auth_enabled(),
            "embedding_provider": self.embedding_provider,
            "embedding_provider_actual": self.get_embedding_provider(),
            "openai_model": self.openai_embedding_model,
            "local_model": self.local_embedding_model,
            "openai_key_configured": self.is_openai_configured(),
            "mcp_transport": self.mcp_transport,
            "mcp_sse_port": self.mcp_sse_port,
        }
