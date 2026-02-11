"""Endee MCP Framework - System tools."""

import time
from typing import Any

from ..types import HealthStatus


async def endee_health_check() -> dict[str, Any]:
    """Check if Endee server is healthy.
    
    Returns:
        Health status information
    """
    from ..server import endee_client, embedding_manager, config
    
    try:
        # Check Endee health
        health = await endee_client.health_check()
        endee_status = "healthy" if health.get("status") == "ok" else "unhealthy"
    except Exception as e:
        endee_status = f"error: {e}"
    
    # Check embedding provider
    provider = embedding_manager.get_provider()
    local_model_loaded = embedding_manager.is_local_model_loaded()
    
    return {
        "status": endee_status,
        "endee_url": config.endee_url,
        "timestamp": int(time.time()),
        "embedding_provider": provider.provider_name,
        "local_model_loaded": local_model_loaded,
    }


async def endee_get_config() -> dict[str, Any]:
    """Get current MCP server configuration.
    
    Returns:
        Configuration information (sanitized)
    """
    from ..server import config, embedding_manager
    
    provider = embedding_manager.get_provider()
    
    return {
        "endee_url": config.endee_url,
        "endee_auth_enabled": config.is_auth_enabled(),
        "embedding_provider": config.embedding_provider,
        "embedding_provider_actual": config.get_embedding_provider(),
        "openai_model": config.openai_embedding_model,
        "local_model": config.local_embedding_model,
        "local_model_dimension": provider.dimension if hasattr(provider, 'dimension') else 0,
        "openai_key_configured": config.is_openai_configured(),
        "mcp_transport": config.mcp_transport,
        "mcp_sse_port": config.mcp_sse_port,
    }
