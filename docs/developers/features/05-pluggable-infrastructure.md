# Developer Guide: Pluggable Infrastructure

A core architectural principle of InsightHub is the use of abstract interfaces and factories to create a pluggable infrastructure layer. This makes it easy to add, remove, or swap out implementations for external services like LLMs, databases, and storage.

This guide explains the pattern and how to extend it.

## The Abstract Interface & Factory Pattern

The pattern is consistent across all infrastructure components (`llm`, `storage`, `vector_stores`, `cache`). Let's use the `llm` component as the canonical example.

1.  **Abstract Base Class (Interface):**
    A file like `llm_provider.py` defines the abstract interface that all concrete implementations must adhere to. For example, it might define an `LlmProvider` abstract class with a method like `generate(prompt: str) -> str`.

2.  **Concrete Implementations:**
    Separate files like `openai_llm_provider.py` or `ollama_llm_provider.py` contain the concrete implementations. Each class in these files inherits from the base `LlmProvider` and implements the abstract methods with provider-specific logic (e.g., making API calls to OpenAI or a local Ollama instance).

3.  **The Factory:**
    A `factory.py` file provides a function (e.g., `get_llm_provider`) that takes a configuration object or a simple string identifier as input. This function contains the `if/elif/else` logic to decide which concrete implementation to instantiate and return.

    ```python
    # In src/infrastructure/llm/factory.py
    from .llm_provider import LlmProvider
    from .openai_llm_provider import OpenAiLlmProvider
    from .ollama_llm_provider import OllamaLlmProvider

    def get_llm_provider(config: LlmConfig) -> LlmProvider:
        if config.provider == "openai":
            return OpenAiLlmProvider(api_key=config.api_key)
        elif config.provider == "ollama":
            return OllamaLlmProvider(base_url=config.base_url)
        # ... other providers
        raise ValueError(f"Unknown LLM provider: {config.provider}")
    ```

## How It's Used

The application's business logic (in the domain services and RAG workflows) never imports a concrete implementation directly. It **only** interacts with the factory.

This means a RAG workflow can get an LLM provider without needing to know if it's OpenAI, Claude, or Ollama. It simply calls the factory and uses the object it receives, confident that it conforms to the `LlmProvider` interface.

## Adding a New Provider

To add a new provider (e.g., a new LLM service called "MegaChat"):

1.  **Create the Implementation File:**
    Create a new file `src/infrastructure/llm/megachat_llm_provider.py`.

2.  **Implement the Interface:**
    Inside the new file, create a class `MegaChatLlmProvider` that inherits from `LlmProvider` and implements all of its abstract methods.

3.  **Update the Factory:**
    Open `src/infrastructure/llm/factory.py` and add a new condition to handle the "megachat" provider. Import your new class and instantiate it when the configuration matches.

The new provider is now available to the entire application without any changes needed in the core business logic. This same process applies to adding a new vector store, cache backend, or storage provider.
