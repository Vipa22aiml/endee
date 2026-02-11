"""Endee MCP Framework - Pydantic models."""

from typing import Any, Literal
from pydantic import BaseModel, Field


class IndexConfig(BaseModel):
    """Configuration for creating an index."""
    name: str = Field(..., description="Unique name for the index")
    dimension: int = Field(..., ge=2, le=16384, description="Vector dimensionality")
    space_type: Literal["cosine", "l2", "ip"] = Field(default="cosine", description="Distance metric")
    precision: Literal["binary", "int8d", "int16d", "float16", "float32"] = Field(
        default="int8d", description="Quantization level"
    )
    sparse_dimension: int | None = Field(default=None, ge=1, description="For hybrid search")
    m: int = Field(default=16, ge=4, le=512, description="HNSW connectivity")
    ef_construction: int = Field(default=128, ge=8, le=4096, description="Build quality")


class IndexInfo(BaseModel):
    """Information about an index."""
    name: str
    dimension: int
    space_type: str
    precision: str
    total_elements: int = 0
    sparse_dim: int = 0
    m: int = 16
    created_at: int = 0


class VectorItem(BaseModel):
    """A vector to upsert."""
    id: str = Field(..., description="Unique identifier")
    vector: list[float] = Field(..., description="Embedding vector")
    meta: dict[str, Any] | None = Field(default=None, description="Metadata")
    filter: dict[str, Any] | None = Field(default=None, description="Filterable fields")
    sparse_indices: list[int] | None = Field(default=None, description="For hybrid search")
    sparse_values: list[float] | None = Field(default=None, description="For hybrid search")


class DocumentItem(BaseModel):
    """A document to upsert with automatic embedding."""
    id: str = Field(..., description="Unique identifier")
    text: str = Field(..., description="Text content to embed")
    meta: dict[str, Any] | None = Field(default=None, description="Metadata")
    filter: dict[str, Any] | None = Field(default=None, description="Filterable fields")


class FilterCondition(BaseModel):
    """A filter condition for search/deletion."""
    field: str
    operator: Literal["$eq", "$in", "$range"]
    value: Any


class SearchQuery(BaseModel):
    """Search query parameters."""
    vector: list[float] | None = Field(default=None, description="Query vector")
    top_k: int = Field(default=10, ge=1, le=4096, description="Number of results")
    filter: list[dict[str, Any]] | None = Field(default=None, description="Filter conditions")
    ef: int = Field(default=128, ge=1, le=1024, description="Search quality")
    include_vectors: bool = Field(default=False, description="Include vector data")


class SearchResult(BaseModel):
    """A single search result."""
    id: str
    similarity: float
    distance: float
    meta: dict[str, Any] | None = None
    filter: dict[str, Any] | None = None
    vector: list[float] | None = None


class BackupInfo(BaseModel):
    """Information about a backup."""
    name: str
    timestamp: int
    size_mb: int


class HealthStatus(BaseModel):
    """Health check response."""
    status: str
    endee_url: str
    timestamp: int
    embedding_provider: str
    local_model_loaded: bool = False
