"""Endee MCP Framework - Index management tools."""

from typing import Any, Literal

from mcp.server import Server

from ..types import IndexConfig


async def endee_create_index(
    name: str,
    dimension: int,
    space_type: Literal["cosine", "l2", "ip"] = "cosine",
    precision: Literal["binary", "int8d", "int16d", "float16", "float32"] = "int8d",
    sparse_dimension: int | None = None,
    m: int = 16,
    ef_construction: int = 128,
) -> dict[str, Any]:
    """Create a new vector index in Endee.
    
    Args:
        name: Unique name for the index
        dimension: Vector dimensionality (2-16384)
        space_type: Distance metric (cosine, l2, ip)
        precision: Quantization level
        sparse_dimension: For hybrid search if > 0
        m: HNSW connectivity (4-512)
        ef_construction: Build quality (8-4096)
    
    Returns:
        Success message
    """
    from ..server import endee_client
    
    config = IndexConfig(
        name=name,
        dimension=dimension,
        space_type=space_type,
        precision=precision,
        sparse_dimension=sparse_dimension,
        m=m,
        ef_construction=ef_construction,
    )
    
    return await endee_client.create_index(config)


async def endee_list_indexes() -> dict[str, Any]:
    """List all available indexes.
    
    Returns:
        List of index information
    """
    from ..server import endee_client
    
    indexes = await endee_client.list_indexes()
    return {"indexes": [idx.model_dump() for idx in indexes]}


async def endee_describe_index(name: str) -> dict[str, Any]:
    """Get detailed information about an index.
    
    Args:
        name: Name of the index
    
    Returns:
        Index details
    """
    from ..server import endee_client
    
    return await endee_client.get_index_info(name)


async def endee_delete_index(name: str, confirm: bool = False) -> dict[str, Any]:
    """Delete an index and all its data.
    
    Args:
        name: Name of the index to delete
        confirm: Must be True to confirm deletion
    
    Returns:
        Success message
    
    Raises:
        ValueError: If confirm is not True
    """
    if not confirm:
        raise ValueError("Must set confirm=True to delete index")
    
    from ..server import endee_client
    
    return await endee_client.delete_index(name)
