"""Endee MCP Framework - Batch import tools."""

import json
import csv
from pathlib import Path
from typing import Any, Literal


async def endee_import_json(
    index_name: str,
    file_path: str,
    id_field: str = "id",
    text_field: str | None = None,
    vector_field: str | None = None,
    meta_fields: list[str] | None = None,
    filter_fields: list[str] | None = None,
    batch_size: int = 100,
    embedding_provider: Literal["openai", "local", "auto"] = "auto",
) -> dict[str, Any]:
    """Import data from a JSON or JSONL file.
    
    Args:
        index_name: Target index name
        file_path: Path to JSON/JSONL file
        id_field: Field to use as ID
        text_field: Field with text to embed (if no vector_field)
        vector_field: Field with pre-computed vectors
        meta_fields: Fields for metadata
        filter_fields: Fields for filtering
        batch_size: Records per batch
        embedding_provider: Embedding provider
    
    Returns:
        Import statistics
    """
    from ..server import endee_client, embedding_manager
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read file
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix == '.jsonl':
            for line in f:
                records.append(json.loads(line))
        else:
            records = json.load(f)
    
    # Process records
    total_imported = 0
    failed = 0
    
    # Get embedding provider if needed
    provider = None
    if text_field and not vector_field:
        provider = embedding_manager.get_provider()
    
    # Process in batches
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        vectors = []
        
        for record in batch:
            try:
                vector_item = {"id": record[id_field]}
                
                # Get vector or text
                if vector_field:
                    vector_item["vector"] = record[vector_field]
                elif text_field:
                    # Will embed later
                    pass
                
                # Add metadata
                if meta_fields:
                    vector_item["meta"] = {
                        field: record.get(field) 
                        for field in meta_fields 
                        if field in record
                    }
                
                # Add filter fields
                if filter_fields:
                    vector_item["filter"] = {
                        field: record.get(field)
                        for field in filter_fields
                        if field in record
                    }
                
                vectors.append(vector_item)
            except Exception as e:
                failed += 1
                continue
        
        # Generate embeddings if needed
        if provider and text_field:
            texts = [record[text_field] for record in batch if text_field in record]
            embeddings = await provider.embed_texts(texts)
            for vec, emb in zip(vectors, embeddings):
                vec["vector"] = emb
        
        # Upsert to Endee
        try:
            await endee_client.upsert_vectors(index_name, vectors)
            total_imported += len(vectors)
        except Exception as e:
            failed += len(vectors)
    
    return {
        "success": True,
        "total_imported": total_imported,
        "failed": failed,
    }


async def endee_import_csv(
    index_name: str,
    file_path: str,
    id_column: str = "id",
    text_column: str | None = None,
    vector_column: str | None = None,
    meta_columns: list[str] | None = None,
    filter_columns: list[str] | None = None,
    delimiter: str = ",",
    batch_size: int = 100,
    embedding_provider: Literal["openai", "local", "auto"] = "auto",
) -> dict[str, Any]:
    """Import data from a CSV file.
    
    Args:
        index_name: Target index name
        file_path: Path to CSV file
        id_column: Column for ID
        text_column: Column with text
        vector_column: Column with vectors
        meta_columns: Columns for metadata
        filter_columns: Columns for filtering
        delimiter: CSV delimiter
        batch_size: Records per batch
        embedding_provider: Embedding provider
    
    Returns:
        Import statistics
    """
    from ..server import endee_client, embedding_manager
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read CSV
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        records = list(reader)
    
    # Process records
    total_imported = 0
    failed = 0
    
    # Get embedding provider if needed
    provider = None
    if text_column and not vector_column:
        provider = embedding_manager.get_provider()
    
    # Process in batches
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        vectors = []
        
        for record in batch:
            try:
                vector_item = {"id": record[id_column]}
                
                # Get vector or text
                if vector_column:
                    # Parse JSON vector
                    vector_item["vector"] = json.loads(record[vector_column])
                elif text_column:
                    # Will embed later
                    pass
                
                # Add metadata
                if meta_columns:
                    vector_item["meta"] = {
                        col: record.get(col)
                        for col in meta_columns
                        if col in record
                    }
                
                # Add filter fields
                if filter_columns:
                    vector_item["filter"] = {
                        col: record.get(col)
                        for col in filter_columns
                        if col in record
                    }
                
                vectors.append(vector_item)
            except Exception as e:
                failed += 1
                continue
        
        # Generate embeddings if needed
        if provider and text_column:
            texts = [record[text_column] for record in batch if text_column in record]
            embeddings = await provider.embed_texts(texts)
            for vec, emb in zip(vectors, embeddings):
                vec["vector"] = emb
        
        # Upsert to Endee
        try:
            await endee_client.upsert_vectors(index_name, vectors)
            total_imported += len(vectors)
        except Exception as e:
            failed += len(vectors)
    
    return {
        "success": True,
        "total_imported": total_imported,
        "failed": failed,
    }
