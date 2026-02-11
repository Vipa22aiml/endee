#!/usr/bin/env python3
"""
Endee MCP Examples - Basic Usage

This script demonstrates how to use the Endee MCP client library
for common vector database operations.

Prerequisites:
    - Endee server running (e.g., via Docker)
    - pip install -e mcp/

Environment:
    ENDEE_URL=http://localhost:8080
    ENDEE_AUTH_TOKEN=your_token (if auth enabled)
"""

import asyncio
import os
from pathlib import Path

# Add mcp/src to path for examples
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp" / "src"))

from endee_mcp.config import Config
from endee_mcp.client import EndeeClient
from endee_mcp.embeddings import EmbeddingManager
from endee_mcp.types import IndexConfig


# ============================================================================
# Configuration
# ============================================================================

ENDEE_URL = os.getenv("ENDEE_URL", "http://localhost:8080")
ENDEE_AUTH_TOKEN = os.getenv("ENDEE_AUTH_TOKEN", "")


# ============================================================================
# Helper Functions
# ============================================================================

def get_client():
    """Create an Endee client."""
    return EndeeClient(
        base_url=ENDEE_URL,
        auth_token=ENDEE_AUTH_TOKEN if ENDEE_AUTH_TOKEN else None
    )


def get_embedding_manager():
    """Create an embedding manager."""
    config = Config.from_env()
    return EmbeddingManager(
        provider_type=config.get_embedding_provider(),
        openai_api_key=config.openai_api_key if config.openai_api_key else None,
        openai_model=config.openai_embedding_model,
        local_model=config.local_embedding_model,
    )


# ============================================================================
# Example 1: Health Check
# ============================================================================

async def example_health_check():
    """Check if Endee server is healthy."""
    print("\n" + "="*60)
    print("Example 1: Health Check")
    print("="*60)
    
    client = get_client()
    
    try:
        health = await client.health_check()
        print(f"✅ Server is healthy!")
        print(f"   Status: {health.get('status')}")
        print(f"   Timestamp: {health.get('timestamp')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    finally:
        await client.close()


# ============================================================================
# Example 2: Index Management
# ============================================================================

async def example_index_management():
    """Create, list, and delete indexes."""
    print("\n" + "="*60)
    print("Example 2: Index Management")
    print("="*60)
    
    client = get_client()
    index_name = "example-docs"
    
    try:
        # 1. List existing indexes
        print("\n1. Listing existing indexes...")
        indexes = await client.list_indexes()
        print(f"   Found {len(indexes)} index(es)")
        for idx in indexes:
            print(f"   - {idx.name} ({idx.dimension}d, {idx.space_type})")
        
        # 2. Create a new index
        print(f"\n2. Creating index '{index_name}'...")
        config = IndexConfig(
            name=index_name,
            dimension=384,  # For all-MiniLM-L6-v2
            space_type="cosine",
            precision="int8d",
            m=16,
            ef_construction=128
        )
        
        try:
            result = await client.create_index(config)
            print(f"   ✅ Index created: {result.get('message')}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ⚠️  Index already exists")
            else:
                raise
        
        # 3. Get index info
        print(f"\n3. Getting index info for '{index_name}'...")
        info = await client.get_index_info(index_name)
        print(f"   Dimension: {info.get('dimension')}")
        print(f"   Space Type: {info.get('space_type')}")
        print(f"   Total Elements: {info.get('total_elements')}")
        print(f"   Precision: {info.get('precision')}")
        
        # 4. List indexes again
        print("\n4. Listing indexes again...")
        indexes = await client.list_indexes()
        print(f"   Found {len(indexes)} index(es)")
        
        print("\n✅ Index management example completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


# ============================================================================
# Example 3: Vector Operations
# ============================================================================

async def example_vector_operations():
    """Insert, retrieve, and delete vectors."""
    print("\n" + "="*60)
    print("Example 3: Vector Operations")
    print("="*60)
    
    client = get_client()
    index_name = "example-docs"
    
    try:
        # Create index if it doesn't exist
        config = IndexConfig(
            name=index_name,
            dimension=384,
            space_type="cosine",
            precision="int8d"
        )
        try:
            await client.create_index(config)
            print(f"✅ Created index '{index_name}'")
        except:
            print(f"ℹ️  Using existing index '{index_name}'")
        
        # 1. Insert vectors
        print("\n1. Inserting vectors...")
        vectors = [
            {
                "id": "doc-001",
                "vector": [0.1] * 384,  # Example 384-dim vector
                "meta": {"title": "Introduction to Vector DBs"},
                "filter": {"category": "tutorial"}
            },
            {
                "id": "doc-002",
                "vector": [0.2] * 384,
                "meta": {"title": "Advanced Search Techniques"},
                "filter": {"category": "advanced"}
            },
            {
                "id": "doc-003",
                "vector": [0.3] * 384,
                "meta": {"title": "Performance Optimization"},
                "filter": {"category": "advanced"}
            }
        ]
        
        result = await client.upsert_vectors(index_name, vectors)
        print(f"   ✅ Inserted vectors: {result}")
        
        # 2. Search
        print("\n2. Searching for similar vectors...")
        query_vector = [0.15] * 384  # Close to doc-001
        results = await client.search(
            index_name=index_name,
            vector=query_vector,
            top_k=3,
            ef=64
        )
        print(f"   Found {len(results)} results:")
        for r in results:
            print(f"   - {r.id}: similarity={r.similarity:.4f}")
        
        # 3. Get specific vector
        print("\n3. Retrieving specific vector...")
        vector = await client.get_vector(index_name, "doc-001")
        if vector:
            print(f"   ✅ Found vector: {vector}")
        else:
            print(f"   ❌ Vector not found")
        
        # 4. Delete a vector
        print("\n4. Deleting vector 'doc-003'...")
        result = await client.delete_vector(index_name, "doc-003")
        print(f"   ✅ Deleted: {result}")
        
        # 5. Delete by filter
        print("\n5. Deleting vectors with category='advanced'...")
        result = await client.delete_by_filter(
            index_name,
            filter_conditions=[{"category": {"$eq": "advanced"}}]
        )
        print(f"   ✅ Deleted: {result}")
        
        print("\n✅ Vector operations example completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


# ============================================================================
# Example 4: Text Search with Embeddings
# ============================================================================

async def example_text_search():
    """Search using text queries with automatic embedding generation."""
    print("\n" + "="*60)
    print("Example 4: Text Search with Embeddings")
    print("="*60)
    
    client = get_client()
    embedding_manager = get_embedding_manager()
    index_name = "example-text"
    
    try:
        # Get embedding provider
        provider = embedding_manager.get_provider()
        print(f"Using embedding provider: {provider.provider_name}")
        print(f"Dimension: {provider.dimension}")
        
        # Create index with correct dimension
        config = IndexConfig(
            name=index_name,
            dimension=provider.dimension,
            space_type="cosine",
            precision="int8d"
        )
        try:
            await client.create_index(config)
            print(f"✅ Created index '{index_name}'")
        except:
            print(f"ℹ️  Using existing index '{index_name}'")
        
        # Insert documents with embeddings
        print("\n1. Inserting documents with automatic embeddings...")
        documents = [
            {
                "id": "recipe-001",
                "text": "How to make authentic Italian pasta with tomato sauce",
                "meta": {"type": "recipe", "cuisine": "italian"},
                "filter": {"difficulty": "easy"}
            },
            {
                "id": "recipe-002",
                "text": "Classic French onion soup recipe with Gruyère cheese",
                "meta": {"type": "recipe", "cuisine": "french"},
                "filter": {"difficulty": "medium"}
            },
            {
                "id": "recipe-003",
                "text": "Quick and easy Japanese ramen noodle soup",
                "meta": {"type": "recipe", "cuisine": "japanese"},
                "filter": {"difficulty": "easy"}
            }
        ]
        
        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        embeddings = await provider.embed_texts(texts)
        
        # Create vectors
        vectors = []
        for doc, embedding in zip(documents, embeddings):
            vectors.append({
                "id": doc["id"],
                "vector": embedding,
                "meta": doc["meta"],
                "filter": doc["filter"]
            })
        
        await client.upsert_vectors(index_name, vectors)
        print(f"   ✅ Inserted {len(vectors)} documents")
        
        # Search with text query
        print("\n2. Searching for 'Italian dinner ideas'...")
        query_embedding = await provider.embed_query("Italian dinner ideas")
        results = await client.search(
            index_name=index_name,
            vector=query_embedding,
            top_k=2
        )
        print(f"   Found {len(results)} results:")
        for r in results:
            meta = r.meta or {}
            print(f"   - {r.id}: {meta.get('type', 'unknown')} ({r.similarity:.4f})")
        
        # Search with filter
        print("\n3. Searching for easy recipes only...")
        results = await client.search(
            index_name=index_name,
            vector=query_embedding,
            top_k=10,
            filter_conditions=[{"difficulty": {"$eq": "easy"}}]
        )
        print(f"   Found {len(results)} easy recipes:")
        for r in results:
            print(f"   - {r.id}: {r.similarity:.4f}")
        
        print("\n✅ Text search example completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


# ============================================================================
# Example 5: Backup Operations
# ============================================================================

async def example_backup_operations():
    """Create and manage backups."""
    print("\n" + "="*60)
    print("Example 5: Backup Operations")
    print("="*60)
    
    client = get_client()
    index_name = "example-docs"
    backup_name = "example-backup"
    
    try:
        # Create index if needed
        config = IndexConfig(
            name=index_name,
            dimension=384,
            space_type="cosine",
            precision="int8d"
        )
        try:
            await client.create_index(config)
        except:
            pass
        
        # 1. List existing backups
        print("\n1. Listing existing backups...")
        backups = await client.list_backups()
        print(f"   Found {len(backups)} backup(s)")
        for b in backups:
            print(f"   - {b}")
        
        # 2. Create backup
        print(f"\n2. Creating backup '{backup_name}'...")
        try:
            result = await client.create_backup(index_name, backup_name)
            print(f"   ✅ Backup created: {result}")
        except Exception as e:
            print(f"   ⚠️  {e}")
        
        # 3. List backups again
        print("\n3. Listing backups again...")
        backups = await client.list_backups()
        print(f"   Found {len(backups)} backup(s)")
        
        # 4. Restore backup (to a new index)
        restored_name = f"{index_name}-restored"
        print(f"\n4. Restoring backup to '{restored_name}'...")
        try:
            result = await client.restore_backup(backup_name, restored_name)
            print(f"   ✅ Restored: {result}")
        except Exception as e:
            print(f"   ⚠️  {e}")
        
        print("\n✅ Backup operations example completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


# ============================================================================
# Example 6: Batch Import from JSON
# ============================================================================

async def example_batch_import():
    """Import data from JSON/JSONL files."""
    print("\n" + "="*60)
    print("Example 6: Batch Import from JSON")
    print("="*60)
    
    import json
    import tempfile
    
    client = get_client()
    index_name = "example-batch"
    
    try:
        # Create sample JSONL file
        print("\n1. Creating sample JSONL file...")
        sample_data = [
            {
                "id": "product-001",
                "name": "Wireless Bluetooth Headphones",
                "description": "Premium over-ear headphones with active noise cancellation",
                "category": "electronics",
                "price": 199.99
            },
            {
                "id": "product-002",
                "name": "Smart Fitness Watch",
                "description": "Track your workouts, heart rate, and sleep patterns",
                "category": "electronics",
                "price": 149.99
            },
            {
                "id": "product-003",
                "name": "Portable Phone Charger",
                "description": "20000mAh power bank for charging on the go",
                "category": "electronics",
                "price": 49.99
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in sample_data:
                f.write(json.dumps(item) + '\n')
            temp_path = f.name
        
        print(f"   ✅ Created: {temp_path}")
        
        # Create index
        config = IndexConfig(
            name=index_name,
            dimension=384,  # Assuming local embeddings
            space_type="cosine"
        )
        try:
            await client.create_index(config)
            print(f"✅ Created index '{index_name}'")
        except:
            print(f"ℹ️  Using existing index '{index_name}'")
        
        # Note: Full batch import would use embedding manager
        # This is a simplified example
        print("\n2. Reading and preparing data for import...")
        
        with open(temp_path, 'r') as f:
            for line in f:
                data = json.loads(line.strip())
                print(f"   - {data['id']}: {data['name']}")
        
        # Cleanup
        os.unlink(temp_path)
        print(f"   ✅ Cleaned up temp file")
        
        print("\n✅ Batch import example completed!")
        print("   (In production, use endee_import_json tool for full import with embeddings)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


# ============================================================================
# Main Runner
# ============================================================================

async def run_all_examples():
    """Run all examples."""
    print("\n" + "="*60)
    print("Endee MCP Examples")
    print("="*60)
    print(f"\nConnecting to: {ENDEE_URL}")
    print(f"Auth enabled: {bool(ENDEE_AUTH_TOKEN)}")
    
    # Run examples
    await example_health_check()
    await example_index_management()
    await example_vector_operations()
    # Skip text search if no embedding provider available
    try:
        await example_text_search()
    except Exception as e:
        print(f"\n⚠️  Skipping text search example: {e}")
    await example_backup_operations()
    await example_batch_import()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


def main():
    """Main entry point."""
    try:
        asyncio.run(run_all_examples())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
