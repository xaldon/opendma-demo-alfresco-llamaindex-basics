"""Build an in-memory index from one Alfresco site and chat with it."""

from __future__ import annotations

import argparse
import sys

from llama_index.core import Settings as LlamaSettings
from llama_index.core import VectorStoreIndex
from llama_index.readers.docling import DoclingReader
from llama_index.readers.opendma import AlfrescoReader

from opendma_demo_alfresco_llamaindex_basics.config import load_settings
from opendma_demo_alfresco_llamaindex_basics.formatting import print_response, print_source_nodes
from opendma_demo_alfresco_llamaindex_basics.models import create_embed_model, create_llm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Load one Alfresco site through OpenDMA and ask questions over an in-memory index."
        )
    )
    parser.add_argument("site", help="Alfresco site short name, for example 'swsdp'.")
    parser.add_argument(
        "--question",
        help="Run one question, print the response, and exit.",
    )
    return parser.parse_args()


def build_index(site: str) -> VectorStoreIndex:
    settings = load_settings()
    LlamaSettings.llm = create_llm(settings)
    LlamaSettings.embed_model = create_embed_model(settings)

    reader = AlfrescoReader(
        endpoint=settings.endpoint,
        username=settings.username,
        password=settings.password,
        sites=[site],
        file_extractor_per_mimetype={
            "application/msword": DoclingReader(),
        },
    )

    print(f"Loading Alfresco site: {site}")
    print("Ingesting content from Alfresco. This can take a while...", flush=True)
    documents = reader.load_data()
    print(f"Loaded LlamaIndex documents: {len(documents)}")

    index = VectorStoreIndex.from_documents(documents)
    print(f"Indexed reference documents: {len(index.ref_doc_info)}")
    docstore_docs = getattr(index.storage_context.docstore, "docs", None)
    if docstore_docs is not None:
        print(f"Indexed nodes: {len(docstore_docs)}")
    print()
    return index


def ask(query_engine, question: str) -> None:
    response = query_engine.query(question)
    print_response(response)
    print_source_nodes(response)


def interactive_loop(query_engine) -> None:
    while True:
        question = input("Question> ").strip()
        if question.lower() in {"exit", "quit"}:
            return
        if not question:
            print('Type "exit" or "quit" to end the application.')
            continue
        ask(query_engine, question)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    index = build_index(args.site)
    query_engine = index.as_query_engine(similarity_top_k=5)

    if args.question:
        ask(query_engine, args.question)
        return

    interactive_loop(query_engine)


if __name__ == "__main__":
    main()
