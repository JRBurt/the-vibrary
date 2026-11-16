"""MCP server exposing search over the vibrary pgvector index.

Run with: python -m src.mcp_server
Then point an MCP client (e.g. Claude Code) at this process over stdio.
"""

from pathlib import Path

from mcp.server.mcpserver import MCPServer

from src import db
from src.embeddings import embed_one

INSTRUCTIONS = (Path(__file__).parent / "server_instructions.md").read_text(encoding="utf-8")

mcp = MCPServer("vibrary", instructions=INSTRUCTIONS)


@mcp.tool()
def search(query: str, collection: str | None = None, top_k: int = 5) -> list[dict]:
    """Search the markdown corpus for chunks relevant to a query.

    Args:
        query: natural-language question or topic to search for.
        collection: optional name to restrict the search (e.g. "glossary",
            "skills"). Call list_collections to see what's available.
        top_k: how many chunks to return, most relevant first.
    """
    query_embedding = embed_one(query)
    with db.get_connection() as conn:
        return db.search(conn, query_embedding, collection=collection, top_k=top_k)


@mcp.tool()
def list_collections() -> list[str]:
    """List the names of collections currently indexed."""
    with db.get_connection() as conn:
        return db.list_collections(conn)


if __name__ == "__main__":
    mcp.run()
