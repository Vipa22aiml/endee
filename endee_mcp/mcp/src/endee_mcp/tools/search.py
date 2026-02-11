"""Endee MCP Framework - Search tools."""

from typing import Any, Literal


async def endee_search(
    index_name: str,
    vector: list[float],
    top_k: int = 10,
    filter: list[dict[str, Any]] | None = None,
    ef: int = 128,
    include_vectors: bool = False,
) -> dict[str, Any]:
    """Search for similar vectors using a query vector.
    
    Args:
        index_name: Name of the index to search
        vector: Query vector
        top_k: Number of results
        filter: Optional filter conditions
        ef: Search quality parameter
        include_vectors: Include vector data
    
    Returns:
        Search results
    """
    from ..server import endee_client
    
    results = await endee_client.search(
        index_name=index_name,
        vector=vector,
        top_k=top_k,
        filter_conditions=filter,
        ef=ef,
        include_vectors=include_vectors,
    )
    
    return {
        "results": [r.model_dump() for r in results],
        "total_results": len(results),
    }


async def endee_search_text(
    index_name: str,
    query: str,
    top_k: int = 10,
    filter: list[dict[str, Any]] | None = None,
    ef: int = 128,
    embedding_provider: Literal["openai", "local", "auto"] = "auto",
    embedding_model: str | None = None,
) -> dict[str, Any]:
    """Search for similar documents using a text query.
    
    Args:
        index_name: Name of the index to search
        query: Search query text
        top_k: Number of results
        filter: Optional filter conditions
        ef: Search quality parameter
        embedding_provider: Which provider to use
        embedding_model: Override default model
    
    Returns:
        Search results with provider info
    """
    from ..server import endee_client, embedding_manager, config
    
    # Get embedding provider
    provider = embedding_manager.get_provider()
    
    # Generate query embedding
    query_vector = await provider.embed_query(query)
    
    # Search
    results = await endee_client.search(
        index_name=index_name,
        vector=query_vector,
        top_k=top_k,
        filter_conditions=filter,
        ef=ef,
        include_vectors=False,
    )
    
    return {
        "results": [r.model_dump() for r in results],
        "total_results": len(results),
        "query_embedding_provider": provider.provider_name,
    }


async def endee_hybrid_search(
    index_name: str,
    query: str,
    top_k: int = 10,
    filter: list[dict[str, Any]] | None = None,
    dense_weight: float = 0.7,
    embedding_provider: Literal["openai", "local", "auto"] = "auto",
) -> dict[str, Any]:
    """Perform hybrid search combining dense and sparse vectors.
    
    Args:
        index_name: Name of the hybrid index
        query: Search query text
        top_k: Number of results
        filter: Optional filter conditions
        dense_weight: Weight for dense vectors (0.0-1.0)
        embedding_provider: Provider for dense vectors
    
    Returns:
        Hybrid search results
    """
    from ..server import endee_client, embedding_manager
    
    # Get embedding provider
    provider = embedding_manager.get_provider()
    
    # Generate dense embedding
    dense_vector = await provider.embed_query(query)
    
    # Generate sparse representation (simple tokenization)
    # In a real implementation, you'd use BM25 or similar
    tokens = query.lower().split()
    sparse_indices = list(range(len(tokens)))
    sparse_values = [1.0] * len(tokens)
    
    # Search with both vectors
    results = await endee_client.search(
        index_name=index_name,
        vector=dense_vector,
        sparse_indices=sparse_indices,
        sparse_values=sparse_values,
        top_k=top_k,
        filter_conditions=filter,
    )
    
    return {
        "results": [r.model_dump() for r in results],
        "total_results": len(results),
        "search_type": "hybrid",
        "dense_weight": dense_weight,
    }
