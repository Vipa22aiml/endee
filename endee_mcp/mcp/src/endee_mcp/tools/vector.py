"""Endee MCP Framework - Vector operation tools."""

from typing import Any, Literal

from ..types import VectorItem, DocumentItem


async def endee_upsert_vectors(
    index_name: str,
    vectors: list[dict[str, Any]],
) -> dict[str, Any]:
    """Insert or update vectors with pre-computed embeddings.
    
    Args:
        index_name: Target index name
        vectors: List of vector objects with id, vector, meta, filter
    
    Returns:
        Upserted count
    """
    from ..server import endee_client
    
    return await endee_client.upsert_vectors(index_name, vectors)


async def endee_upsert_documents(
    index_name: str,
    documents: list[dict[str, Any]],
    embedding_provider: Literal["openai", "local", "auto"] = "auto",
    embedding_model: str | None = None,
) -> dict[str, Any]:
    """Insert documents with automatic embedding generation.
    
    Args:
        index_name: Target index name
        documents: List of documents with id, text, meta, filter
        embedding_provider: Which provider to use
        embedding_model: Override default model
    
    Returns:
        Upserted count and provider info
    """
    from ..server import endee_client, embedding_manager, config
    
    # Get embedding provider
    provider = embedding_manager.get_provider()
    
    # Extract texts
    texts = [doc["text"] for doc in documents]
    
    # Generate embeddings
    embeddings = await provider.embed_texts(texts)
    
    # Create vector items
    vectors = []
    for doc, embedding in zip(documents, embeddings):
        vector_item = {
            "id": doc["id"],
            "vector": embedding,
        }
        if "meta" in doc:
            vector_item["meta"] = doc["meta"]
        if "filter" in doc:
            vector_item["filter"] = doc["filter"]
        vectors.append(vector_item)
    
    # Upsert to Endee
    result = await endee_client.upsert_vectors(index_name, vectors)
    
    return {
        **result,
        "embedding_provider": provider.provider_name,
        "embedding_model": embedding_model or config.openai_embedding_model if provider.provider_name.startswith("openai") else config.local_embedding_model,
    }


async def endee_get_vector(
    index_name: str,
    vector_id: str,
    include_vector: bool = False,
) -> dict[str, Any] | None:
    """Retrieve a vector by ID.
    
    Args:
        index_name: Name of the index
        vector_id: ID of the vector
        include_vector: Whether to include raw vector data
    
    Returns:
        Vector info or None if not found
    """
    from ..server import endee_client
    
    return await endee_client.get_vector(index_name, vector_id)


async def endee_delete_vector(
    index_name: str,
    vector_id: str,
) -> dict[str, Any]:
    """Delete a vector by ID.
    
    Args:
        index_name: Name of the index
        vector_id: ID of the vector
    
    Returns:
        Success message
    """
    from ..server import endee_client
    
    return await endee_client.delete_vector(index_name, vector_id)


async def endee_delete_by_filter(
    index_name: str,
    filter: list[dict[str, Any]],
) -> dict[str, Any]:
    """Delete vectors matching filter criteria.
    
    Args:
        index_name: Name of the index
        filter: Filter conditions
    
    Returns:
        Deleted count
    """
    from ..server import endee_client
    
    return await endee_client.delete_by_filter(index_name, filter)


async def endee_update_filters(
    index_name: str,
    updates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Update filter fields for existing vectors.
    
    Args:
        index_name: Name of the index
        updates: List of update objects with 'id' and 'filter' fields
            Example: [{"id": "doc1", "filter": {"category": "updated"}}]
    
    Returns:
        Updated count
    """
    from ..server import endee_client
    
    return await endee_client.update_filters(index_name, updates)
