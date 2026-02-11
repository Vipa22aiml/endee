"""Endee MCP Framework - Local embedding provider using sentence-transformers."""

import asyncio
from typing import Any

from .base import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embedding provider using sentence-transformers."""
    
    MODEL_DIMENSIONS = {
        "sentence-transformers/all-MiniLM-L6-v2": 384,
        "sentence-transformers/all-mpnet-base-v2": 768,
        "BAAI/bge-small-en-v1.5": 384,
        "BAAI/bge-base-en-v1.5": 768,
    }
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", preload: bool = False):
        """Initialize local provider.
        
        Args:
            model_name: HuggingFace model name
            preload: Whether to load model immediately
        """
        self.model_name = model_name
        self._model = None
        self._dimension = self.MODEL_DIMENSIONS.get(model_name, 384)
        
        if preload:
            self._load_model()
    
    @property
    def provider_name(self) -> str:
        return f"local-{self.model_name.split('/')[-1]}"
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def _load_model(self):
        """Lazy load the sentence-transformers model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                import torch
                
                # Use GPU if available
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._model = SentenceTransformer(self.model_name, device=device)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
    
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts locally."""
        self._load_model()
        
        # Run in thread pool to not block
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, 
            lambda: self._model.encode(texts, convert_to_numpy=True).tolist()
        )
        
        return embeddings
    
    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None
