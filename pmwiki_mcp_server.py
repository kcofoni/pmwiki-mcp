"""
MCP (Model Context Protocol) server for PmWiki.

This server exposes PmWiki pages via the MCP protocol using SSE (Server-Sent Events)
transport. It allows an LLM to interact with the wiki to read, search, and list pages.

Features:
- Read wiki pages
- Search text across the wiki
- List available pages
- Expose pages as MCP resources
"""
import asyncio
import logging
import os
import re

import mcp.types as types
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Resource, TextContent, Tool
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp_server = Server("pmwiki-server")

# The directory will be mounted from the Docker volume
WIKI_DIR = os.getenv("WIKI_DIR", "/wiki_data")


def parse_pmwiki_file(filepath):
    """Parse a PmWiki file and extract its content"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract text after "text="
        match = re.search(r"text=(.+?)(?:\n[a-z]+=|$)", content, re.DOTALL)
        if match:
            text = match.group(1)
            # Decode PmWiki format
            text = text.replace("%0a", "\n")
            text = text.replace("%25", "%")
            text = text.replace("%22", '"')
            text = text.replace("%3c", "<")
            text = text.replace("%3e", ">")
            return text
        return ""
    except Exception as e:
        logger.error("Error reading %s: %s", filepath, str(e))
        return f"Error reading file: {str(e)}"


def get_page_title(filename):
    """Extract page title from filename"""
    return filename.replace(".", "/")


@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """List all wiki pages as resources"""
    resources = []

    if not os.path.exists(WIKI_DIR):
        logger.warning("Directory %s does not exist", WIKI_DIR)
        return resources

    try:
        for filename in os.listdir(WIKI_DIR):
            if filename.startswith("."):
                continue

            filepath = os.path.join(WIKI_DIR, filename)
            if os.path.isfile(filepath):
                resources.append(
                    Resource(
                        uri=f"pmwiki://{filename}",
                        name=get_page_title(filename),
                        mimeType="text/plain",
                        description=f"Wiki page: {get_page_title(filename)}",
                    )
                )

        logger.info("Found %d wiki pages", len(resources))
    except Exception as e:
        logger.error("Error listing resources: %s", str(e))

    return resources


@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Read the content of a wiki page"""
    if not uri.startswith("pmwiki://"):
        raise ValueError("Invalid URI")

    filename = uri.replace("pmwiki://", "")
    filepath = os.path.join(WIKI_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Page {filename} not found")

    content = parse_pmwiki_file(filepath)
    return content


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_wiki",
            description="Search for text across all PmWiki pages. Returns pages containing the search text with a context snippet.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for in the wiki",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Case-sensitive search (default: false)",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="read_page",
            description="Read the complete content of a specific wiki page. Use the format 'Group.PageName' or 'Group/PageName'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_name": {
                        "type": "string",
                        "description": "Page name (e.g., Main.HomePage or Main/HomePage)",
                    }
                },
                "required": ["page_name"],
            },
        ),
        Tool(
            name="list_pages",
            description="List all available pages in the wiki, optionally filtered by group.",
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {
                        "type": "string",
                        "description": "Group name to filter pages (optional)",
                    }
                },
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute a tool"""

    if name == "search_wiki":
        query = arguments["query"]
        case_sensitive = arguments.get("case_sensitive", False)
        results = []

        if not case_sensitive:
            query = query.lower()

        if not os.path.exists(WIKI_DIR):
            return [
                TextContent(
                    type="text",
                    text=f"Error: Wiki directory {WIKI_DIR} does not exist",
                )
            ]

        for filename in os.listdir(WIKI_DIR):
            if filename.startswith("."):
                continue

            filepath = os.path.join(WIKI_DIR, filename)
            if not os.path.isfile(filepath):
                continue

            content = parse_pmwiki_file(filepath)
            search_content = content if case_sensitive else content.lower()

            if query in search_content:
                # Find context around the first occurrence
                index = search_content.find(query)
                start = max(0, index - 100)
                end = min(len(content), index + 100)
                snippet = content[start:end].strip()

                results.append(
                    {"page": get_page_title(filename), "snippet": f"...{snippet}..."}
                )

        if not results:
            return [
                TextContent(type="text", text=f"No results found for '{query}'")
            ]

        result_text = f"Found {len(results)} result(s) for '{query}':\n\n"
        for r in results[:10]:  # Limit to 10 results
            result_text += f"**{r['page']}**\n{r['snippet']}\n\n"

        if len(results) > 10:
            result_text += f"\n... and {len(results) - 10} more results"

        return [TextContent(type="text", text=result_text)]

    elif name == "read_page":
        page_name = arguments["page_name"]
        # Convert Main/HomePage to Main.PageName
        filename = page_name.replace("/", ".")
        filepath = os.path.join(WIKI_DIR, filename)

        if not os.path.exists(filepath):
            # Try to list similar pages
            similar = []
            search_term = page_name.lower().replace("/", ".").replace(".", "")

            for fname in os.listdir(WIKI_DIR):
                if search_term in fname.lower().replace(".", ""):
                    similar.append(get_page_title(fname))

            suggestion = ""
            if similar:
                suggestion = "\n\nSimilar pages found:\n" + "\n".join(
                    [f"- {p}" for p in similar[:5]]
                )

            return [
                TextContent(
                    type="text",
                    text=f"Page '{page_name}' not found.{suggestion}\n\nUse 'list_pages' to see all available pages.",
                )
            ]

        content = parse_pmwiki_file(filepath)
        return [TextContent(type="text", text=f"# {page_name}\n\n{content}")]

    elif name == "list_pages":
        group_filter = arguments.get("group")
        pages = []

        if not os.path.exists(WIKI_DIR):
            return [
                TextContent(
                    type="text",
                    text=f"Error: Wiki directory {WIKI_DIR} does not exist",
                )
            ]

        for filename in sorted(os.listdir(WIKI_DIR)):
            if filename.startswith("."):
                continue

            filepath = os.path.join(WIKI_DIR, filename)
            if not os.path.isfile(filepath):
                continue

            page_title = get_page_title(filename)

            if group_filter:
                if not page_title.startswith(f"{group_filter}/"):
                    continue

            pages.append(page_title)

        if not pages:
            msg = "No pages found"
            if group_filter:
                msg += f" in group '{group_filter}'"
            return [TextContent(type="text", text=msg)]

        # Group pages by group
        grouped = {}
        for page in pages:
            if "/" in page:
                group = page.split("/")[0]
            else:
                group = "Root"

            if group not in grouped:
                grouped[group] = []
            grouped[group].append(page)

        result_text = f"Available pages ({len(pages)}):\n\n"
        for group, group_pages in sorted(grouped.items()):
            result_text += f"**{group}** ({len(group_pages)} pages)\n"
            for page in group_pages[:10]:  # Limit display
                result_text += f"  - {page}\n"
            if len(group_pages) > 10:
                result_text += f"  ... and {len(group_pages) - 10} more pages\n"
            result_text += "\n"

        return [TextContent(type="text", text=result_text)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def run_sse_server():
    """Start the server in SSE mode"""
    # Create the SSE transport
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        """Handle SSE connections (GET /sse)"""
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server.run(
                streams[0],
                streams[1],
                mcp_server.create_initialization_options(),
            )
        return Response()

    # Create the Starlette application
    app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    config = uvicorn.Config(app, host="0.0.0.0", port=3000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    logger.info("Starting PmWiki MCP server in SSE mode on port 3000")
    logger.info("Wiki directory: %s", WIKI_DIR)

    asyncio.run(run_sse_server())
