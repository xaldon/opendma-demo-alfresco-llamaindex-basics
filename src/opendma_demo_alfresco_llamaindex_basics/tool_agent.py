"""Use AlfrescoToolSpec with a LlamaIndex tool-calling agent."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Any

from llama_index.core.agent import FunctionAgent
from llama_index.core.agent.workflow import ToolCall, ToolCallResult
from llama_index.readers.docling import DoclingReader
from llama_index.tools.opendma import AlfrescoToolSpec

from opendma_demo_alfresco_llamaindex_basics.config import load_settings
from opendma_demo_alfresco_llamaindex_basics.formatting import shorten
from opendma_demo_alfresco_llamaindex_basics.models import create_llm

SYSTEM_PROMPT = """
You answer questions using documents stored in Alfresco.

In some cases, it is sufficient to locate the relevant documents in the repository
and use metadata to answer the user's question.

In other cases, the requested information is in the documents and you need to read
the documents to answer the question. Reading documents is more expensive than
listing children, listing sites, searching, or getting metadata. Use it carefully.

Use alfresco_list_sites to discover sites.
Use opendma_search to search for candidate documents.
Use opendma_list_children to browse folders.
Use opendma_get_metadata to inspect a candidate document.
Use opendma_read_text to read document text when metadata is not enough.

Do not answer factual repository questions unless the answer is supported by tool
results. If the repository does not contain enough information, say so.
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask a tool-calling agent to browse Alfresco through OpenDMA."
    )
    parser.add_argument(
        "--question",
        help="Run one question, print the response, and exit.",
    )
    return parser.parse_args()


def create_agent() -> FunctionAgent:
    settings = load_settings()
    tool_spec = AlfrescoToolSpec(
        endpoint=settings.endpoint,
        username=settings.username,
        password=settings.password,
        file_extractor_per_mimetype={
            "application/msword": DoclingReader(),
        },
    )
    return FunctionAgent(
        name="AlfrescoOpenDMAAgent",
        description="Answers questions by browsing Alfresco content exposed through OpenDMA.",
        system_prompt=SYSTEM_PROMPT,
        tools=tool_spec.to_tool_list(),
        llm=create_llm(settings),
        timeout=120,
        verbose=False,
    )


def _raw_tool_output(event: ToolCallResult) -> Any:
    tool_output = getattr(event, "tool_output", None)
    if tool_output is None:
        return event
    return getattr(tool_output, "raw_output", tool_output)


async def run_question(agent: FunctionAgent, question: str) -> None:
    print(f"Question: {question}")
    print()

    handler = agent.run(question)
    async for event in handler.stream_events():
        if isinstance(event, ToolCall):
            print(f"Tool call: {event.tool_name}")
            print(f"Args: {event.tool_kwargs}")
            print()
        elif isinstance(event, ToolCallResult):
            print(f"Tool result: {event.tool_name}")
            print(shorten(str(_raw_tool_output(event)), 1200))
            print()

    response = await handler
    print("Final answer:")
    print(response)
    print()


async def interactive_loop(agent: FunctionAgent) -> None:
    while True:
        question = input("Question> ").strip()
        if question.lower() in {"exit", "quit"}:
            return
        if not question:
            print('Type "exit" or "quit" to end the application.')
            continue
        await run_question(agent, question)


async def async_main() -> None:
    args = parse_args()
    agent = create_agent()

    if args.question:
        await run_question(agent, args.question)
        return

    await interactive_loop(agent)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
