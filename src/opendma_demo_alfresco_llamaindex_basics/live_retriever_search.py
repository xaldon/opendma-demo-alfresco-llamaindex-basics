"""Search Alfresco live through OpenDMA with AlfrescoRetriever."""

from __future__ import annotations

import argparse
import sys

from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.docling import DoclingReader
from llama_index.retrievers.opendma import AlfrescoRetriever

from opendma_demo_alfresco_llamaindex_basics.config import load_settings
from opendma_demo_alfresco_llamaindex_basics.formatting import format_node_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run live Alfresco full-text search through OpenDMA."
    )
    parser.add_argument("query", help="Full-text query to send to Alfresco through OpenDMA.")
    parser.add_argument("--site", help="Optional Alfresco site short name.")
    parser.add_argument(
        "--k",
        type=int,
        default=8,
        help="Maximum number of LlamaIndex nodes to return. Default: 8.",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    if args.k <= 0:
        raise SystemExit("--k must be greater than 0")

    settings = load_settings()
    retriever = AlfrescoRetriever(
        endpoint=settings.endpoint,
        username=settings.username,
        password=settings.password,
        sites=[args.site] if args.site else None,
        file_extractor_per_mimetype={
            "application/msword": DoclingReader(),
        },
        transformations=[
            SentenceSplitter(chunk_size=1024, chunk_overlap=100),
        ],
        similarity_top_k=args.k,
    )

    nodes = retriever.retrieve(args.query)
    print(f"Retrieved nodes: {len(nodes)}")
    print()
    for index, node_with_score in enumerate(nodes, start=1):
        print(format_node_result(index, node_with_score.node))
        print()
        print("-" * 80)
        print()


if __name__ == "__main__":
    main()
