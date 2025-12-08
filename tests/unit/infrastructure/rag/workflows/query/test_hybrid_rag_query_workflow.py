"""Unit tests for Hybrid RAG query workflow with Reciprocal Rank Fusion."""

import unittest
from unittest.mock import MagicMock

from src.infrastructure.rag.workflows.query.hybrid_rag_query_workflow import HybridRagQueryWorkflow
from src.infrastructure.types.rag import ChunkData


class TestHybridRagQueryWorkflow(unittest.TestCase):
    """Unit tests for HybridRagQueryWorkflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.vector_workflow = MagicMock()
        self.graph_workflow = MagicMock()
        self.workflow = HybridRagQueryWorkflow(
            vector_workflow=self.vector_workflow,
            graph_workflow=self.graph_workflow,
            rrf_k=60,
        )

    def test_reciprocal_rank_fusion_basic(self):
        """Test RRF with non-overlapping chunks from both sources."""
        vector_chunks = [
            ChunkData(
                chunk_id="v1", document_id="doc1", text="vector chunk 1", score=0.9, metadata={}
            ),
            ChunkData(
                chunk_id="v2", document_id="doc1", text="vector chunk 2", score=0.8, metadata={}
            ),
        ]
        graph_chunks = [
            ChunkData(
                chunk_id="g1", document_id="doc2", text="graph chunk 1", score=0.85, metadata={}
            ),
            ChunkData(
                chunk_id="g2", document_id="doc2", text="graph chunk 2", score=0.75, metadata={}
            ),
        ]

        result = self.workflow._reciprocal_rank_fusion(vector_chunks, graph_chunks)

        # Should have all 4 chunks
        self.assertEqual(len(result), 4)
        # All chunks should be present
        chunk_ids = {chunk.chunk_id for chunk in result}
        self.assertEqual(chunk_ids, {"v1", "v2", "g1", "g2"})

    def test_reciprocal_rank_fusion_with_duplicates(self):
        """Test RRF with overlapping chunks from both sources."""
        shared_chunk = ChunkData(
            chunk_id="shared", document_id="doc1", text="shared chunk", score=0.7, metadata={}
        )

        vector_chunks = [
            ChunkData(
                chunk_id="v1", document_id="doc1", text="vector chunk 1", score=0.9, metadata={}
            ),
            shared_chunk,
            ChunkData(
                chunk_id="v2", document_id="doc1", text="vector chunk 2", score=0.6, metadata={}
            ),
        ]
        graph_chunks = [
            shared_chunk,
            ChunkData(
                chunk_id="g1", document_id="doc2", text="graph chunk 1", score=0.8, metadata={}
            ),
        ]

        result = self.workflow._reciprocal_rank_fusion(vector_chunks, graph_chunks)

        # Should have 4 unique chunks (shared chunk appears in both but counted once)
        self.assertEqual(len(result), 4)
        chunk_ids = [chunk.chunk_id for chunk in result]
        self.assertEqual(set(chunk_ids), {"v1", "shared", "v2", "g1"})

        # Shared chunk should be ranked higher due to appearing in both lists
        # It appears at rank 1 in vector (0-indexed) and rank 0 in graph
        # RRF score: 1/(60+2) + 1/(60+1) = 0.0161 + 0.0164 = 0.0325
        # v1 only in vector at rank 0: 1/(60+1) = 0.0164
        # g1 only in graph at rank 1: 1/(60+2) = 0.0161
        # So order should be: shared, v1, g1, v2
        self.assertEqual(chunk_ids[0], "shared")

    def test_reciprocal_rank_fusion_ranking(self):
        """Test that RRF properly ranks items appearing in both lists higher."""
        # Create chunks with specific ranking scenarios
        chunk_a = ChunkData(
            chunk_id="a", document_id="doc1", text="chunk a", score=1.0, metadata={}
        )
        chunk_b = ChunkData(
            chunk_id="b", document_id="doc1", text="chunk b", score=0.9, metadata={}
        )
        chunk_c = ChunkData(
            chunk_id="c", document_id="doc1", text="chunk c", score=0.8, metadata={}
        )

        # Vector: [a, b, c] - a is rank 0, b is rank 1, c is rank 2
        vector_chunks = [chunk_a, chunk_b, chunk_c]

        # Graph: [c, b] - c is rank 0, b is rank 1
        graph_chunks = [chunk_c, chunk_b]

        result = self.workflow._reciprocal_rank_fusion(vector_chunks, graph_chunks)

        # Expected RRF scores:
        # c: 1/(60+3) + 1/(60+1) = 0.0159 + 0.0164 = 0.0323 (appears in both)
        # b: 1/(60+2) + 1/(60+2) = 0.0161 + 0.0161 = 0.0322 (appears in both)
        # a: 1/(60+1) = 0.0164 (only in vector)

        # Order should be: c, b, a (c and b appear in both, so ranked higher)
        chunk_ids = [chunk.chunk_id for chunk in result]
        self.assertEqual(chunk_ids, ["c", "b", "a"])

    def test_execute_calls_both_workflows(self):
        """Test that execute calls both vector and graph workflows."""
        vector_chunks = [
            ChunkData(
                chunk_id="v1", document_id="doc1", text="vector chunk", score=0.9, metadata={}
            ),
        ]
        graph_chunks = [
            ChunkData(
                chunk_id="g1", document_id="doc2", text="graph chunk", score=0.8, metadata={}
            ),
        ]

        self.vector_workflow.execute.return_value = vector_chunks
        self.graph_workflow.execute.return_value = graph_chunks

        result = self.workflow.execute("test query", top_k=5)

        # Should call both workflows with 2x top_k
        self.vector_workflow.execute.assert_called_once_with("test query", 10, None)
        self.graph_workflow.execute.assert_called_once_with("test query", 10, None)

        # Should return fused results
        self.assertEqual(len(result), 2)
        chunk_ids = {chunk.chunk_id for chunk in result}
        self.assertEqual(chunk_ids, {"v1", "g1"})

    def test_execute_limits_to_top_k(self):
        """Test that execute returns only top_k results after fusion."""
        vector_chunks = [
            ChunkData(
                chunk_id=f"v{i}",
                document_id="doc1",
                text=f"vector chunk {i}",
                score=0.9 - i * 0.1,
                metadata={},
            )
            for i in range(10)
        ]
        graph_chunks = [
            ChunkData(
                chunk_id=f"g{i}",
                document_id="doc2",
                text=f"graph chunk {i}",
                score=0.85 - i * 0.1,
                metadata={},
            )
            for i in range(10)
        ]

        self.vector_workflow.execute.return_value = vector_chunks
        self.graph_workflow.execute.return_value = graph_chunks

        result = self.workflow.execute("test query", top_k=5)

        # Should return only 5 results despite having 20 total
        self.assertEqual(len(result), 5)

    def test_execute_with_filters(self):
        """Test that filters are passed to both workflows."""
        filters = {"workspace_id": "123"}
        self.vector_workflow.execute.return_value = []
        self.graph_workflow.execute.return_value = []

        self.workflow.execute("test query", top_k=5, filters=filters)

        # Filters should be passed to both workflows
        self.vector_workflow.execute.assert_called_once_with("test query", 10, filters)
        self.graph_workflow.execute.assert_called_once_with("test query", 10, filters)


if __name__ == "__main__":
    unittest.main()
