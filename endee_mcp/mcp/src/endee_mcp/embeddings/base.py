"""Endee MCP Framework - Embedding provider base class."""

from abc import ABC, abstractmethod
from typing import Literal


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimension of the embeddings."""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass


class NoneProvider(EmbeddingProvider):
    """Provider that returns None (when embeddings are disabled)."""
    
    @property
    def provider_name(self) -> str:
        return "none"
    
    @property
    def dimension(self) -> int:
        return 0
    
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("Embedding provider is disabled")
    
    async def embed_query(self, text: str) -> list[float]:
        raise RuntimeError("Embedding provider is disabled")
