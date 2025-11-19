#!/usr/bin/env python3
"""
Test script to verify shared package imports work correctly.

Run from the shared package directory:
    poetry run python test_imports.py
"""

print("Testing shared package imports...\n")

# Test type imports
print("1. Testing type imports...")
try:
    from shared.types import (
        Chunk,
        ChunkerConfig,
        Document,
        GraphEdge,
        GraphNode,
        MetadataValue,
        PrimitiveValue,
        RagConfig,
        RetrievalResult,
        SearchResult,
    )

    print("   ✓ All types imported successfully")
    print(f"   - Document: {Document.__name__}")
    print(f"   - Chunk: {Chunk.__name__}")
    print(f"   - GraphNode: {GraphNode.__name__}")
    print(f"   - GraphEdge: {GraphEdge.__name__}")
except ImportError as e:
    print(f"   ✗ Failed to import types: {e}")
    exit(1)

# Test Vector RAG interface imports
print("\n2. Testing Vector RAG interface imports...")
try:
    from shared.interfaces.vector import (
        Chunker,
        ContextBuilder,
        DocumentParser,
        EmbeddingEncoder,
        LLM,
        OutputFormatter,
        Ranker,
        VectorIndex,
        VectorRetriever,
    )

    print("   ✓ All Vector RAG interfaces imported successfully")
    print(f"   - DocumentParser: {DocumentParser.__name__}")
    print(f"   - Chunker: {Chunker.__name__}")
    print(f"   - EmbeddingEncoder: {EmbeddingEncoder.__name__}")
    print(f"   - VectorIndex: {VectorIndex.__name__}")
    print(f"   - VectorRetriever: {VectorRetriever.__name__}")
    print(f"   - Ranker: {Ranker.__name__}")
    print(f"   - ContextBuilder: {ContextBuilder.__name__}")
    print(f"   - LLM: {LLM.__name__}")
    print(f"   - OutputFormatter: {OutputFormatter.__name__}")
except ImportError as e:
    print(f"   ✗ Failed to import Vector RAG interfaces: {e}")
    exit(1)

# Test data type instantiation
print("\n3. Testing data type instantiation...")
try:
    doc = Document(
        id="doc_1",
        workspace_id="workspace_1",
        title="Test Document",
        content="This is a test document.",
        metadata={"author": "Test Author", "year": 2025},
    )
    print(f"   ✓ Created Document: {doc.id} - {doc.title}")

    chunk = Chunk(
        id="chunk_1",
        document_id="doc_1",
        text="This is a test chunk.",
        metadata={"index": 0, "source": "test"},
        vector=None,
    )
    print(f"   ✓ Created Chunk: {chunk.id}")

    node = GraphNode(id="node_1", labels=["Entity", "Person"], properties={"name": "John Doe"})
    print(f"   ✓ Created GraphNode: {node.id} with labels {node.labels}")

    edge = GraphEdge(
        id="edge_1",
        source="node_1",
        target="node_2",
        label="knows",
        properties={"since": 2020},
    )
    print(f"   ✓ Created GraphEdge: {edge.label} from {edge.source} to {edge.target}")

except Exception as e:
    print(f"   ✗ Failed to instantiate data types: {e}")
    exit(1)

# Test interface usage
print("\n4. Testing interface usage (abstract methods)...")
try:
    from abc import ABCMeta

    assert isinstance(DocumentParser, ABCMeta), "DocumentParser should be abstract"
    assert isinstance(Chunker, ABCMeta), "Chunker should be abstract"
    assert isinstance(EmbeddingEncoder, ABCMeta), "EmbeddingEncoder should be abstract"
    assert isinstance(VectorIndex, ABCMeta), "VectorIndex should be abstract"
    print("   ✓ All interfaces are properly abstract")
except AssertionError as e:
    print(f"   ✗ Interface check failed: {e}")
    exit(1)

print("\n" + "=" * 50)
print("✅ All import tests passed!")
print("=" * 50)
print("\nThe shared package is correctly configured and ready to use.")
print("\nNext steps:")
print("  1. Use 'from shared.types import Document, Chunk' in server/workers")
print("  2. Use 'from shared.interfaces.vector import EmbeddingEncoder' for interfaces")
print("  3. Implement concrete classes that inherit from these interfaces")
