"""Endee MCP Framework - Main server module."""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import Config
from .client import EndeeClient
from .embeddings import EmbeddingManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
config: Config | None = None
endee_client: EndeeClient | None = None
embedding_manager: EmbeddingManager | None = None


async def main():
    """Main entry point for MCP server."""
    global config, endee_client, embedding_manager
    
    # Load configuration
    config = Config.from_env()
    logger.info(f"Starting Endee MCP server with transport: {config.mcp_transport}")
    
    # Initialize Endee client
    endee_client = EndeeClient(
        base_url=config.endee_url,
        auth_token=config.endee_auth_token if config.endee_auth_token else None
    )
    
    # Initialize embedding manager
    embedding_manager = EmbeddingManager(
        provider_type=config.get_embedding_provider(),
        openai_api_key=config.openai_api_key if config.openai_api_key else None,
        openai_model=config.openai_embedding_model,
        local_model=config.local_embedding_model,
        preload_local=config.preload_local_model,
    )
    
    # Create MCP server
    server = Server("endee-mcp")
    
    # Register tools
    from .tools import index, vector, search, batch, backup, system
    
    # Index management tools
    server.tool()(index.endee_create_index)
    server.tool()(index.endee_list_indexes)
    server.tool()(index.endee_describe_index)
    server.tool()(index.endee_delete_index)
    
    # Vector operation tools
    server.tool()(vector.endee_upsert_vectors)
    server.tool()(vector.endee_upsert_documents)
    server.tool()(vector.endee_get_vector)
    server.tool()(vector.endee_delete_vector)
    server.tool()(vector.endee_delete_by_filter)
    server.tool()(vector.endee_update_filters)
    
    # Search tools
    server.tool()(search.endee_search)
    server.tool()(search.endee_search_text)
    server.tool()(search.endee_hybrid_search)
    
    # Batch import tools
    server.tool()(batch.endee_import_json)
    server.tool()(batch.endee_import_csv)
    
    # Backup tools
    server.tool()(backup.endee_create_backup)
    server.tool()(backup.endee_list_backups)
    server.tool()(backup.endee_restore_backup)
    server.tool()(backup.endee_delete_backup)
    
    # System tools
    server.tool()(system.endee_health_check)
    server.tool()(system.endee_get_config)
    
    # Start server
    if config.mcp_transport == "stdio":
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    else:
        # SSE transport
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        
        sse = SseServerTransport("/messages")
        
        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )
        
        app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/messages", endpoint=sse.handle_post_message),
            ],
        )
        
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=config.mcp_sse_port)
    
    # Cleanup
    if endee_client:
        await endee_client.close()


if __name__ == "__main__":
    asyncio.run(main())
