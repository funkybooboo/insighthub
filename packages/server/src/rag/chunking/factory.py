"""
Factory for creating chunking instances
"""

from src.rag.chunking.base import BaseChunker, ChunkingStrategy
from src.rag.chunking.text_chunkers import (
    CharacterChunker,
    SemanticChunker,
    SentenceChunker,
    WordChunker,
)


def get_chunker(
    strategy: str | ChunkingStrategy, chunk_size: int = 500, chunk_overlap: int = 50
) -> BaseChunker:
    """
    Factory function to create chunkers based on strategy.

    Args:
        strategy: Chunking strategy name or enum
        chunk_size: Target size for chunks
        chunk_overlap: Overlap between chunks

    Returns:
        Configured chunker instance

    Raises:
        ValueError: If strategy is not recognized

    Examples:
        >>> chunker = get_chunker("sentence", chunk_size=500)
        >>> chunker = get_chunker(ChunkingStrategy.CHARACTER, chunk_size=1000)
    """
    # Convert string to enum if needed
    if isinstance(strategy, str):
        try:
            strategy_enum = ChunkingStrategy(strategy.lower())
        except ValueError as e:
            valid_strategies = [s.value for s in ChunkingStrategy]
            raise ValueError(
                f"Invalid chunking strategy: {strategy}. "
                f"Valid options: {valid_strategies}"
            ) from e
    else:
        strategy_enum = strategy

    # Map strategy to chunker class
    chunker_map: dict[ChunkingStrategy, type[BaseChunker]] = {
        ChunkingStrategy.CHARACTER: CharacterChunker,
        ChunkingStrategy.SENTENCE: SentenceChunker,
        ChunkingStrategy.WORD: WordChunker,
        ChunkingStrategy.SEMANTIC: SemanticChunker,
    }

    chunker_class = chunker_map.get(strategy_enum)
    if chunker_class is None:
        raise ValueError(f"No chunker implemented for strategy: {strategy_enum}")

    return chunker_class(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def list_chunking_strategies() -> list[str]:
    """
    Get list of available chunking strategies.

    Returns:
        List of strategy names
    """
    return [strategy.value for strategy in ChunkingStrategy]
