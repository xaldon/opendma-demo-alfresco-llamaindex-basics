"""Configuration shared by the sample applications."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    endpoint: str
    username: str
    password: str
    chat_model: str
    embedding_model: str


def load_settings() -> Settings:
    """Load tutorial-friendly defaults from environment variables."""
    return Settings(
        endpoint=os.environ.get("ALFRESCO_OPENDMA_ENDPOINT", "http://localhost:7070/opendma/alf"),
        username=os.environ.get("ALFRESCO_USERNAME", "admin"),
        password=os.environ.get("ALFRESCO_PASSWORD", "admin"),
        chat_model=os.environ.get("LLAMA_CHAT_MODEL", "openai:gpt-4o-mini"),
        embedding_model=os.environ.get(
            "LLAMA_EMBEDDING_MODEL",
            "openai:text-embedding-3-large",
        ),
    )
