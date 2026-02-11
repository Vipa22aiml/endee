"""Endee MCP Framework - Test suite."""

import asyncio
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from endee_mcp.config import Config
from endee_mcp.types import (
    IndexConfig,
    IndexInfo,
    VectorItem,
    DocumentItem,
    FilterCondition,
    SearchQuery,
    SearchResult,
    BackupInfo,
    HealthStatus,
)
from endee_mcp.client import EndeeClient, EndeeError
from endee_mcp.embeddings.base import EmbeddingProvider, NoneProvider
from endee_mcp.embeddings.openai import OpenAIEmbeddingProvider
from endee_mcp.embeddings.local import LocalEmbeddingProvider
from endee_mcp.embeddings import EmbeddingManager


# ============================================================================
# Configuration Tests
# ============================================================================

class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.endee_url == "http://localhost:8080"
        assert config.endee_auth_token == ""
        assert config.embedding_provider == "auto"
        assert config.openai_embedding_model == "text-embedding-3-small"
        assert config.local_embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.mcp_transport == "stdio"
        assert config.mcp_sse_port == 3000
        assert config.preload_local_model is False
    
    def test_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("ENDEE_URL", "http://endee:8080")
        monkeypatch.setenv("ENDEE_AUTH_TOKEN", "test-token")
        monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        monkeypatch.setenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        monkeypatch.setenv("MCP_TRANSPORT", "sse")
        monkeypatch.setenv("MCP_SSE_PORT", "5000")
        monkeypatch.setenv("PRELOAD_LOCAL_MODEL", "true")
        
        config = Config.from_env()
        assert config.endee_url == "http://endee:8080"
        assert config.endee_auth_token == "test-token"
        assert config.embedding_provider == "openai"
        assert config.openai_api_key == "sk-test"
        assert config.openai_embedding_model == "text-embedding-3-large"
        assert config.local_embedding_model == "BAAI/bge-small-en-v1.5"
        assert config.mcp_transport == "sse"
        assert config.mcp_sse_port == 5000
        assert config.preload_local_model is True
    
    def test_is_openai_configured(self):
        """Test OpenAI configuration check."""
        config = Config()
        assert config.is_openai_configured() is False
        
        config.openai_api_key = "sk-test"
        assert config.is_openai_configured() is True
    
    def test_is_auth_enabled(self):
        """Test auth enabled check."""
        config = Config()
        assert config.is_auth_enabled() is False
        
        config.endee_auth_token = "test-token"
        assert config.is_auth_enabled() is True
    
    def test_get_embedding_provider_auto_with_openai(self):
        """Test auto provider selection with OpenAI key."""
        config = Config(embedding_provider="auto", openai_api_key="sk-test")
        assert config.get_embedding_provider() == "openai"
    
    def test_get_embedding_provider_auto_without_openai(self):
        """Test auto provider selection without OpenAI key."""
        config = Config(embedding_provider="auto", openai_api_key="")
        assert config.get_embedding_provider() == "local"
    
    def test_get_embedding_provider_explicit(self):
        """Test explicit provider selection."""
        config = Config(embedding_provider="local")
        assert config.get_embedding_provider() == "local"
        
        config = Config(embedding_provider="none")
        assert config.get_embedding_provider() == "none"


# ============================================================================
# Type Model Tests
# ============================================================================

class TestIndexConfig:
    """Test IndexConfig model."""
    
    def test_valid_config(self):
        """Test valid index configuration."""
        config = IndexConfig(
            name="test-index",
            dimension=384,
            space_type="cosine",
            precision="int8d",
            m=16,
            ef_construction=128
        )
        assert config.name == "test-index"
        assert config.dimension == 384
        assert config.space_type == "cosine"
        assert config.precision == "int8d"
        assert config.m == 16
        assert config.ef_construction == 128
    
    def test_defaults(self):
        """Test default values."""
        config = IndexConfig(name="test", dimension=384)
        assert config.space_type == "cosine"
        assert config.precision == "int8d"
        assert config.m == 16
        assert config.ef_construction == 128
        assert config.sparse_dimension is None
    
    def test_dimension_validation(self):
        """Test dimension validation."""
        with pytest.raises(Exception):
            IndexConfig(name="test", dimension=1)  # Too small
        
        with pytest.raises(Exception):
            IndexConfig(name="test", dimension=20000)  # Too large
    
    def test_m_validation(self):
        """Test M parameter validation."""
        with pytest.raises(Exception):
            IndexConfig(name="test", dimension=384, m=2)  # Too small
        
        with pytest.raises(Exception):
            IndexConfig(name="test", dimension=384, m=1000)  # Too large


class TestSearchResult:
    """Test SearchResult model."""
    
    def test_valid_result(self):
        """Test valid search result."""
        result = SearchResult(
            id="doc1",
            similarity=0.95,
            distance=0.05,
            meta={"title": "Test Doc"},
            filter={"category": "test"}
        )
        assert result.id == "doc1"
        assert result.similarity == 0.95
        assert result.distance == 0.05
        assert result.meta == {"title": "Test Doc"}


# ============================================================================
# Embedding Provider Tests
# ============================================================================

class TestNoneProvider:
    """Test NoneProvider (disabled embeddings)."""
    
    def test_properties(self):
        """Test provider properties."""
        provider = NoneProvider()
        assert provider.provider_name == "none"
        assert provider.dimension == 0
    
    @pytest.mark.asyncio
    async def test_embed_texts_raises(self):
        """Test that embed_texts raises error."""
        provider = NoneProvider()
        with pytest.raises(RuntimeError, match="disabled"):
            await provider.embed_texts(["test"])
    
    @pytest.mark.asyncio
    async def test_embed_query_raises(self):
        """Test that embed_query raises error."""
        provider = NoneProvider()
        with pytest.raises(RuntimeError, match="disabled"):
            await provider.embed_query("test")


class TestOpenAIEmbeddingProvider:
    """Test OpenAI embedding provider."""
    
    def test_init(self):
        """Test provider initialization."""
        provider = OpenAIEmbeddingProvider(api_key="sk-test", model="text-embedding-3-small")
        assert provider.provider_name == "openai-text-embedding-3-small"
        assert provider.dimension == 1536
        assert provider.model == "text-embedding-3-small"
    
    def test_dimensions(self):
        """Test dimensions for different models."""
        small = OpenAIEmbeddingProvider(api_key="test", model="text-embedding-3-small")
        assert small.dimension == 1536
        
        large = OpenAIEmbeddingProvider(api_key="test", model="text-embedding-3-large")
        assert large.dimension == 3072
        
        ada = OpenAIEmbeddingProvider(api_key="test", model="text-embedding-ada-002")
        assert ada.dimension == 1536
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        provider = OpenAIEmbeddingProvider(api_key="test")
        tokens = provider.estimate_tokens(["hello world", "test"])
        assert tokens > 0  # Rough estimate: ~3 tokens


class TestLocalEmbeddingProvider:
    """Test Local embedding provider."""
    
    def test_init(self):
        """Test provider initialization."""
        provider = LocalEmbeddingProvider(model_name="sentence-transformers/all-MiniLM-L6-v2")
        assert provider.provider_name == "local-all-MiniLM-L6-v2"
        assert provider.dimension == 384
        assert not provider.is_loaded()
    
    def test_dimensions(self):
        """Test dimensions for different models."""
        mini = LocalEmbeddingProvider(model_name="sentence-transformers/all-MiniLM-L6-v2")
        assert mini.dimension == 384
        
        mpnet = LocalEmbeddingProvider(model_name="sentence-transformers/all-mpnet-base-v2")
        assert mpnet.dimension == 768


class TestEmbeddingManager:
    """Test EmbeddingManager."""
    
    def test_none_provider(self):
        """Test creating None provider."""
        manager = EmbeddingManager(provider_type="none")
        provider = manager.get_provider()
        assert provider.provider_name == "none"
    
    def test_openai_provider(self):
        """Test creating OpenAI provider."""
        manager = EmbeddingManager(
            provider_type="openai",
            openai_api_key="sk-test",
            openai_model="text-embedding-3-small"
        )
        provider = manager.get_provider()
        assert provider.provider_name == "openai-text-embedding-3-small"
    
    def test_local_provider(self):
        """Test creating Local provider."""
        manager = EmbeddingManager(
            provider_type="local",
            local_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        provider = manager.get_provider()
        assert provider.provider_name == "local-all-MiniLM-L6-v2"
    
    def test_auto_with_openai_key(self):
        """Test auto selection with OpenAI key."""
        manager = EmbeddingManager(
            provider_type="auto",
            openai_api_key="sk-test"
        )
        provider = manager.get_provider()
        assert provider.provider_name.startswith("openai")
    
    def test_auto_without_openai_key(self):
        """Test auto selection without OpenAI key."""
        manager = EmbeddingManager(provider_type="auto", openai_api_key=None)
        provider = manager.get_provider()
        assert provider.provider_name.startswith("local")
    
    def test_openai_without_key_raises(self):
        """Test that OpenAI provider requires key."""
        manager = EmbeddingManager(provider_type="openai", openai_api_key=None)
        with pytest.raises(ValueError, match="API key not configured"):
            manager.get_provider()


# ============================================================================
# Client Tests
# ============================================================================

class TestEndeeClient:
    """Test Endee HTTP client."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return EndeeClient(base_url="http://localhost:8080")
    
    @pytest.fixture
    def auth_client(self):
        """Create authenticated test client."""
        return EndeeClient(
            base_url="http://localhost:8080",
            auth_token="test-token"
        )
    
    def test_init(self, client):
        """Test client initialization."""
        assert client.base_url == "http://localhost:8080"
        assert client.auth_token is None
    
    def test_init_with_auth(self, auth_client):
        """Test client initialization with auth."""
        assert auth_client.auth_token == "test-token"
    
    def test_get_headers_no_auth(self, client):
        """Test headers without auth."""
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert "Authorization" not in headers
    
    def test_get_headers_with_auth(self, auth_client):
        """Test headers with auth."""
        headers = auth_client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "test-token"
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = Mock()
        
        with patch.object(client.client, 'get', return_value=mock_response):
            result = await client.health_check()
            assert result["status"] == "ok"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring running Endee server."""
    
    @pytest.fixture
    async def client(self):
        """Create real client for integration tests."""
        url = os.getenv("ENDEE_URL", "http://localhost:8080")
        token = os.getenv("ENDEE_AUTH_TOKEN")
        client = EndeeClient(base_url=url, auth_token=token)
        yield client
        await client.close()
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self, client):
        """Test real health check."""
        try:
            result = await client.health_check()
            assert result["status"] == "ok"
        except Exception as e:
            pytest.skip(f"Endee server not available: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
