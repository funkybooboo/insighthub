"""Utility functions and data for RAG embedding options."""

AVAILABLE_EMBEDDERS = {
    "nomic-embed-text": {
        "label": "Nomic Embed Text",
        "description": "Nomic AI embedding model (274M params)",
    },
    "all-MiniLM-L6-v2": {
        "label": "MiniLM",
        "description": "Sentence-BERT embedding model",
    },
    "mxbai-embed-large": {
        "label": "MxBai Embed Large",
        "description": "Large multilingual embedding model",
    },
    "openai": {
        "label": "OpenAI Embeddings",
        "description": "OpenAI embedding models",
    },
    "ollama": {
        "label": "Ollama Embeddings",
        "description": "Ollama embedding models",
    },
    "huggingface": {
        "label": "HuggingFace Embeddings",
        "description": "HuggingFace embedding models",
    },
}


def get_available_embedders() -> list[dict[str, str]]:
    """Get list of available embedding algorithms."""
    return [
        {
            "value": key,
            "label": info["label"],
            "description": info["description"],
        }
        for key, info in AVAILABLE_EMBEDDERS.items()
    ]
