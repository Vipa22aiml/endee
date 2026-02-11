"""Endee MCP Framework."""

__version__ = "0.1.0"
__all__ = ["Config", "EndeeClient", "EmbeddingManager"]

from .config import Config
from .client import EndeeClient
from .embeddings import EmbeddingManager
