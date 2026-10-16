"""Small model factory for the examples.

The examples keep OpenAI as the active provider. Other providers usually need
different LlamaIndex packages and constructors, so this file is intentionally
small and explicit rather than pretending all providers share one config format.
"""

from __future__ import annotations

from opendma_demo_alfresco_llamaindex_basics.config import Settings


def _split_provider_model(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise ValueError(
            f"Model value {value!r} must use the format '<provider>:<model>', "
            "for example 'openai:gpt-4o-mini'."
        )
    provider, model = value.split(":", 1)
    provider = provider.strip().lower()
    model = model.strip()
    if not provider or not model:
        raise ValueError(
            f"Model value {value!r} must use the format '<provider>:<model>', "
            "for example 'openai:gpt-4o-mini'."
        )
    return provider, model


def create_llm(settings: Settings):
    """Create the chat model configured for these examples."""
    provider, model = _split_provider_model(settings.chat_model)
    if provider == "openai":
        from llama_index.llms.openai import OpenAI

        return OpenAI(model=model, temperature=0)

    # Examples for extending this file if you add the optional packages:
    #
    # if provider == "anthropic":
    #     from llama_index.llms.anthropic import Anthropic
    #     return Anthropic(model=model, temperature=0)
    #
    # if provider == "gemini":
    #     from llama_index.llms.gemini import Gemini
    #     return Gemini(model=model, temperature=0)

    raise ValueError(
        f"Unsupported chat provider {provider!r}. "
        "This sample enables OpenAI by default. Extend models.py for other providers."
    )


def create_embed_model(settings: Settings):
    """Create the embedding model configured for these examples."""
    provider, model = _split_provider_model(settings.embedding_model)
    if provider == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding

        return OpenAIEmbedding(model=model)

    # Example for extending this file if you add the optional package:
    #
    # if provider == "gemini":
    #     from llama_index.embeddings.gemini import GeminiEmbedding
    #     return GeminiEmbedding(model_name=model)

    raise ValueError(
        f"Unsupported embedding provider {provider!r}. "
        "This sample enables OpenAI by default. Extend models.py for other providers."
    )
