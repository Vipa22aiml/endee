"""Endee MCP Framework - Embedding manager."""

from typing import Literal

from .base import EmbeddingProvider, NoneProvider
from .openai import OpenAIEmbeddingProvider
from .local import LocalEmbeddingProvider


class EmbeddingManager:
    """Factory and manager for embedding providers."""
    
    def __init__(
        self,
        provider_type: Literal["auto", "openai", "local", "none"],
        openai_api_key: str | None = None,
        openai_model: str = "text-embedding-3-small",
        local_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        preload_local: bool = False,
    ):
        """Initialize embedding manager.
        
        Args:
            provider_type: Type of provider to use
            openai_api_key: OpenAI API key
            openai_model: OpenAI model name
            local_model: Local model name
            preload_local: Whether to preload local model
        """
        self.provider_type = provider_type
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.local_model = local_model
        self.preload_local = preload_local
        self._provider: EmbeddingProvider | None = None
    
    def get_provider(self) -> EmbeddingProvider:
        """Get the appropriate embedding provider.
        
        Returns:
            EmbeddingProvider instance
        """
        if self._provider is not None:
            return self._provider
        
        # Determine actual provider type
        if self.provider_type == "auto":
            if self.openai_api_key:
                actual_type = "openai"
            else:
                actual_type = "local"
        else:
            actual_type = self.provider_type
        
        # Create provider
        if actual_type == "none":
            self._provider = NoneProvider()
        elif actual_type == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self._provider = OpenAIEmbeddingProvider(
                api_key=self.openai_api_key,
                model=self.openai_model
            )
        elif actual_type == "local":
            self._provider = LocalEmbeddingProvider(
                model_name=self.local_model,
                preload=self.preload_local
            )
        else:
            raise ValueError(f"Unknown provider type: {actual_type}")
        
        return self._provider
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.get_provider().dimension
    
    def get_provider_name(self) -> str:
        """Get the name of the current provider."""
        return self.get_provider().provider_name
    
    def is_local_model_loaded(self) -> bool:
        """Check if local model is loaded (if using local provider)."""
        provider = self.get_provider()
        if isinstance(provider, LocalEmbeddingProvider):
            return provider.is_loaded()
        return False
