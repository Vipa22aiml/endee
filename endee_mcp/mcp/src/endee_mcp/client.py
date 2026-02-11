"""Endee MCP Framework - Endee HTTP client."""

import json
from typing import Any

import httpx

from .types import IndexConfig, SearchResult


class EndeeError(Exception):
    """Base exception for Endee client errors."""
    pass


class EndeeClient:
    """Async HTTP client for Endee Vector Database."""
    
    def __init__(self, base_url: str, auth_token: str | None = None):
        """Initialize the client.
        
        Args:
            base_url: Endee server URL (e.g., http://localhost:8080)
            auth_token: Optional authentication token
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_headers(self) -> dict[str, str]:
        """Get request headers with auth if configured."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = self.auth_token
        return headers
    
    async def health_check(self) -> dict[str, Any]:
        """Check if Endee server is healthy."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/health"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/stats"
        )
        response.raise_for_status()
        return response.json()
    
    async def create_index(self, config: IndexConfig) -> dict[str, Any]:
        """Create a new index."""
        payload = {
            "index_name": config.name,
            "dim": config.dimension,
            "space_type": config.space_type,
            "precision": config.precision,
            "M": config.m,
            "ef_con": config.ef_construction,
        }
        if config.sparse_dimension:
            payload["sparse_dim"] = config.sparse_dimension
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/index/create",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return {"success": True, "message": response.text}
    
    async def list_indexes(self) -> list[IndexConfig]:
        """List all indexes."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/index/list",
            headers=self._get_headers()
        )
        response.raise_for_status()
        data = response.json()
        return [IndexConfig(**idx) for idx in data.get("indexes", [])]
    
    async def get_index_info(self, name: str) -> dict[str, Any]:
        """Get information about an index."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/index/{name}/info",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_index(self, name: str) -> dict[str, Any]:
        """Delete an index."""
        response = await self.client.delete(
            f"{self.base_url}/api/v1/index/{name}/delete",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return {"success": True, "message": response.text}
    
    async def upsert_vectors(
        self, 
        index_name: str, 
        vectors: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Upsert vectors into an index."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/index/{index_name}/vector/insert",
            headers={**self._get_headers(), "Content-Type": "application/json"},
            json=vectors
        )
        response.raise_for_status()
        return {"success": response.status_code == 200}
    
    async def get_vector(
        self, 
        index_name: str, 
        vector_id: str
    ) -> dict[str, Any] | None:
        """Get a vector by ID."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/index/{index_name}/vector/get",
            headers=self._get_headers(),
            json={"id": vector_id}
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        # Response is msgpack, need to handle separately
        return {"raw": response.content}
    
    async def delete_vector(self, index_name: str, vector_id: str) -> dict[str, Any]:
        """Delete a vector by ID."""
        response = await self.client.delete(
            f"{self.base_url}/api/v1/index/{index_name}/vector/{vector_id}/delete",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return {"success": True, "message": response.text}
    
    async def delete_by_filter(
        self, 
        index_name: str, 
        filter_conditions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Delete vectors matching filter."""
        response = await self.client.delete(
            f"{self.base_url}/api/v1/index/{index_name}/vectors/delete",
            headers=self._get_headers(),
            json={"filter": filter_conditions}
        )
        response.raise_for_status()
        return {"success": True, "deleted_count": int(response.text.split()[0])}
    
    async def search(
        self,
        index_name: str,
        vector: list[float] | None = None,
        sparse_indices: list[int] | None = None,
        sparse_values: list[float] | None = None,
        top_k: int = 10,
        filter_conditions: list[dict[str, Any]] | None = None,
        ef: int = 128,
        include_vectors: bool = False
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        payload: dict[str, Any] = {
            "k": top_k,
            "ef": ef,
            "include_vectors": include_vectors,
        }
        
        if vector:
            payload["vector"] = vector
        
        if sparse_indices and sparse_values:
            payload["sparse_indices"] = sparse_indices
            payload["sparse_values"] = sparse_values
        
        if filter_conditions:
            payload["filter"] = json.dumps(filter_conditions)
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/index/{index_name}/search",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        # Response is msgpack, parse it
        return self._parse_search_response(response.content)
    
    def _parse_search_response(self, data: bytes) -> list[SearchResult]:
        """Parse msgpack search response."""
        try:
            import msgpack
            results = msgpack.unpackb(data, raw=False)
            return [SearchResult(**r) for r in results]
        except ImportError:
            # Fallback if msgpack not available
            return []
    
    async def create_backup(self, index_name: str, backup_name: str) -> dict[str, Any]:
        """Create a backup of an index."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/index/{index_name}/backup",
            headers=self._get_headers(),
            json={"name": backup_name}
        )
        response.raise_for_status()
        return {"success": True, "message": response.text}
    
    async def list_backups(self) -> list[str]:
        """List all backups."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/backups",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json().get("backups", [])
    
    async def restore_backup(
        self, 
        backup_name: str, 
        target_index_name: str
    ) -> dict[str, Any]:
        """Restore a backup to a new index."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/backups/{backup_name}/restore",
            headers=self._get_headers(),
            json={"target_index_name": target_index_name}
        )
        response.raise_for_status()
        return {"success": True, "message": response.text}
    
    async def delete_backup(self, backup_name: str) -> dict[str, Any]:
        """Delete a backup."""
        response = await self.client.delete(
            f"{self.base_url}/api/v1/backups/{backup_name}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return {"success": True, "message": response.text}
    
    async def update_filters(
        self,
        index_name: str,
        updates: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update filters for vectors.
        
        Args:
            index_name: Name of the index
            updates: List of {id, filter} objects
        
        Returns:
            Updated count
        """
        response = await self.client.post(
            f"{self.base_url}/api/v1/index/{index_name}/filters/update",
            headers=self._get_headers(),
            json={"updates": updates}
        )
        response.raise_for_status()
        return {"success": True, "message": response.text}

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
