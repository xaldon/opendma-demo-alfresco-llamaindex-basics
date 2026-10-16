"""Console formatting helpers for the sample applications."""

from __future__ import annotations

import re
from typing import Any

METADATA_KEYS = [
    "opendma:Title",
    "opendma:CheckedOut",
    "alfresco:Site",
    "alfresco:Path",
    "alfresco:cm:name",
    "alfresco:cm:creator",
    "alfresco:cm:accessed",
    "content_state",
]


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def shorten(text: str, max_length: int = 800) -> str:
    compact = normalize_whitespace(text)
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."


def format_document_metadata(metadata: dict[str, Any]) -> str:
    lines = []
    for key in METADATA_KEYS:
        value = metadata.get(key)
        if value is not None:
            lines.append(f"{key}: {value}")
    return "\n".join(lines) if lines else "No selected metadata available."


def format_node_result(index: int, node: Any, max_content_length: int = 800) -> str:
    metadata = getattr(node, "metadata", {}) or {}
    content = node.get_content() if hasattr(node, "get_content") else str(node)
    title = metadata.get("opendma:Title") or metadata.get("alfresco:cm:name") or "Untitled"
    site = metadata.get("alfresco:Site") or ""
    path = metadata.get("alfresco:Path") or ""
    content_state = metadata.get("content_state") or ""

    lines = [
        f"Result {index}",
        f"Title: {title}",
    ]
    if site:
        lines.append(f"Site: {site}")
    if path:
        lines.append(f"Path: {path}")
    if content_state:
        lines.append(f"Content state: {content_state}")
    lines.extend(["Content:", shorten(content, max_content_length)])
    return "\n".join(lines)


def print_response(response: Any) -> None:
    print()
    print("Answer:")
    print(response)
    print()


def print_source_nodes(response: Any, max_sources: int = 3) -> None:
    source_nodes = getattr(response, "source_nodes", None)
    if not source_nodes:
        return

    print("Sources:")
    for index, node_with_score in enumerate(source_nodes[:max_sources], start=1):
        node = getattr(node_with_score, "node", node_with_score)
        print(format_node_result(index, node, max_content_length=300))
        print()
