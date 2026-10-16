# opendma-demo-alfresco-llamaindex-basics

This repository contains the sample applications for the article
[Connect LlamaIndex to Alfresco with OpenDMA: Reader, Retriever, and Agent Tools](https://dev.to/stefankopfxaldon/connect-llamaindex-to-alfresco-with-opendma-reader-retriever-and-agent-tools-285b).

Here you can find three small Python applications showing how to use Alfresco content from LlamaIndex through OpenDMA:

- `alfresco-index-chat`: load one Alfresco site with `AlfrescoReader`, build an in-memory `VectorStoreIndex`, and ask questions over it
- `alfresco-live-search`: search Alfresco live with `AlfrescoRetriever`
- `alfresco-tool-agent`: let a LlamaIndex tool-calling agent browse Alfresco with `AlfrescoToolSpec`

The examples assume that Alfresco is already running and that it is exposed through an OpenDMA REST endpoint.

## Prerequisites

- Python 3.10 or newer
- `uv`
- a running Alfresco system
- an OpenDMA REST endpoint for Alfresco, expected at `http://localhost:7070/opendma/alf`
- an OpenAI API key for the default model configuration

The examples use `admin/admin` as default credentials because this matches the Alfresco tutorial setup. Do not use this as production guidance.

## Running an OpenDMA Endpoint for Alfresco

The applications need an OpenDMA REST endpoint for Alfresco. The quickest way to map Alfresco to the OpenDMA data model and expose an OpenDMA REST endpoint is to run the ECI Server. It is available free of charge for non-production use.

Start it with Docker Compose:

```bash
git clone https://github.com/xaldon/eci-server.git
cd eci-server/docker_compose
docker compose up -d
```

After the service is running:

1. Open the web UI at `http://localhost:7070`.
2. Initialise the admin account.
3. Accept the license agreement.
4. Install a free-of-charge license key.
5. Navigate to "Admin" > "Connections".
6. Add a new connection to `Alfresco Content Services`.
7. Choose "Automatically detect parameters with Smart Setup" for your Alfresco Content Services as target server.
   (If you are running Alfresco in docker as well, use `host.docker.internal`)
8. Save the new connection as `Alfresco @ <hostname>`.
9. Navigate to "Admin" > "REST Endpoints".
10. Add a new REST Endpoint.
11. Set the slug to `opendma/alf`.
12. Select the `Alfresco @ <hostname>` connection.
13. Keep the proposed "Inbound Authentication" ("HTTP Basic" and "Propagate Inbound").
14. Save the new REST Endpoint.

The examples expect the OpenDMA endpoint at:

```text
http://localhost:7070/opendma/alf
```

To verify this REST endpoint, open `http://localhost:7070/opendma/alf/` with a trailing slash in a web browser and authenticate with your Alfresco credentials (`admin/admin` by default).

## Configuration

The applications read configuration from environment variables:

```bash
export ALFRESCO_OPENDMA_ENDPOINT="http://localhost:7070/opendma/alf"
export ALFRESCO_USERNAME="admin"
export ALFRESCO_PASSWORD="admin"
export OPENAI_API_KEY="..."
export LLAMA_CHAT_MODEL="openai:gpt-4o-mini"
export LLAMA_EMBEDDING_MODEL="openai:text-embedding-3-large"
```

PowerShell:

```powershell
$env:ALFRESCO_OPENDMA_ENDPOINT = "http://localhost:7070/opendma/alf"
$env:ALFRESCO_USERNAME = "admin"
$env:ALFRESCO_PASSWORD = "admin"
$env:OPENAI_API_KEY = "..."
$env:LLAMA_CHAT_MODEL = "openai:gpt-4o-mini"
$env:LLAMA_EMBEDDING_MODEL = "openai:text-embedding-3-large"
```

The defaults already use the endpoint and credentials shown above. `OPENAI_API_KEY` must be set for the examples that call an LLM or embeddings.

Model strings currently support OpenAI by default:

```text
openai:gpt-4o-mini
openai:text-embedding-3-large
```

If you want to use another provider, extend `src/opendma_demo_alfresco_llamaindex_basics/models.py` with the provider-specific LlamaIndex constructor and dependencies.

## Install

From this directory:

```bash
uv sync
```

This sample project currently uses the local `../llama-index-opendma/packages/...` integration packages through `tool.uv.sources`. After the matching OpenDMA LlamaIndex packages are published to PyPI, those local source entries can be replaced with ordinary version constraints.

## Example 1: Index Chat With `AlfrescoReader`

Load one Alfresco site into an in-memory `VectorStoreIndex` and ask questions over the indexed content.

Interactive mode:

```bash
uv run alfresco-index-chat swsdp
```

Single question:

```bash
uv run alfresco-index-chat swsdp --question "Who attended the meeting in January 2011?"
```

After ingestion, the application prints only counts: loaded LlamaIndex documents, indexed reference documents, and indexed nodes when available. In interactive mode, type `exit` or `quit` to end the application.

This example is intentionally in-memory. A production application would normally persist the index and ingest only new or changed documents.

## Example 2: Search Alfresco Live With `AlfrescoRetriever`

Search Alfresco live through OpenDMA without building a vector store:

```bash
uv run alfresco-live-search "meeting notes"
```

Restrict the search to one Alfresco site and set the top-k node limit:

```bash
uv run alfresco-live-search "meeting notes" --site swsdp --k 8
```

Without `--site`, the search runs across the repository exposed by the OpenDMA endpoint.

This is Alfresco full-text search via AFTS through OpenDMA. It is not semantic vector search. The `--k` value maps to `similarity_top_k`, which limits returned LlamaIndex nodes; it is not a vector similarity ranking.

## Example 3: Tool-Calling Agent With `AlfrescoToolSpec`

Run an agent that can list Alfresco sites, search, inspect metadata, browse folders, and read selected text chunks:

```bash
uv run alfresco-tool-agent
```

Single question:

```bash
uv run alfresco-tool-agent --question "Where can I find the meeting notes of the web site design project?"
```

In interactive mode, type `exit` or `quit` to end the application.

The application prints tool calls and compact tool results before the final answer so you can see how the agent navigates the repository.

## Security Notes

These examples default to `admin/admin` because that is convenient for the Alfresco sample setup. In production, use effective-user authentication or identity forwarding where repository permissions and governance markings matter.

If an OpenDMA endpoint is called with a shared technical or admin account, your application still has to enforce user-level authorization itself.

## Mapping To The Article

- `alfresco-index-chat` maps to the `AlfrescoReader` section.
- `alfresco-live-search` maps to the `AlfrescoRetriever` section.
- `alfresco-tool-agent` maps to the `AlfrescoToolSpec` section.

## Further reading:

- OpenDMA: https://opendma.org/
- ECI Server: https://xaldon.com/products/eci-server
- LlamaIndex OpenDMA integration: https://github.com/OpenDMA/llama-index-opendma
- Tutorials: https://github.com/OpenDMA/llama-index-opendma/tree/main/docs/tutorials
- Reader documentation: https://github.com/OpenDMA/llama-index-opendma/blob/main/docs/Reader.md
- Retriever documentation: https://github.com/OpenDMA/llama-index-opendma/blob/main/docs/Retriever.md
- ToolSpec documentation: https://github.com/OpenDMA/llama-index-opendma/blob/main/docs/ToolSpec.md
