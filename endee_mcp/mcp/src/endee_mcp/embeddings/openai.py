"""Endee MCP Framework - OpenAI embedding provider."""

import asyncio
from typing import Any

from .base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI API-based embedding provider."""
    
    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002)
        """
        self.api_key = api_key
        self.model = model
        self._client = None
        self._dimension = self.MODEL_DIMENSIONS.get(model, 1536)
    
    @property
    def provider_name(self) -> str:
        return f"openai-{self.model}"
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. "
                    "Install with: pip install openai"
                )
        return self._client
    
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts using OpenAI API."""
        client = self._get_client()
        
        # OpenAI has a limit of 2048 texts per request
        batch_size = 2048
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = await client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings
                embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(embeddings)
                
            except Exception as e:
                raise RuntimeError(f"OpenAI embedding failed: {e}")
        
        return all_embeddings
    
    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]
    
    def estimate_tokens(self, texts: list[str]) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters
        total_chars = sum(len(text) for text in texts)
        return total_chars // 4
