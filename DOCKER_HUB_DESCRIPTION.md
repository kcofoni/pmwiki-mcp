# PmWiki MCP Server

A Model Context Protocol (MCP) server that provides LLMs with read-only access to PmWiki content through a standardized interface.

## What is this?

This Docker image runs an MCP server that exposes your PmWiki pages via the Model Context Protocol using Server-Sent Events (SSE) transport. It enables AI assistants like Claude to read, search, and interact with your wiki content.

## Features

- **Read-only Access**: Safe, read-only mounting of your wiki.d directory
- **Full-text Search**: Search across all wiki pages with case-sensitive option
- **Resource Exposure**: All wiki pages exposed as MCP resources with `pmwiki://` URIs
- **Easy Integration**: Works with Claude Desktop and any MCP-compatible client

## Quick Start

```bash
docker run -d \
  --name pmwiki-mcp-server \
  -p 3000:3000 \
  -v /path/to/your/wiki.d:/wiki_data:ro \
  -e WIKI_DIR=/wiki_data \
  kcofoni/pmwiki-mcp:latest
```

Replace `/path/to/your/wiki.d` with the actual path to your PmWiki data directory.

## Docker Compose

```yaml
version: '3.8'

services:
  pmwiki-mcp:
    image: kcofoni/pmwiki-mcp:latest
    container_name: pmwiki-mcp-server
    ports:
      - "3000:3000"
    volumes:
      - /path/to/your/wiki.d:/wiki_data:ro
    environment:
      - WIKI_DIR=/wiki_data
    restart: unless-stopped
```

## Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pmwiki": {
      "command": "mcp-proxy",
      "args": [
        "--transport=sse",
        "http://localhost:3000/sse"
      ]
    }
  }
}
```

Replace `localhost` with your Docker host IP if running remotely.

## Available Tools

1. **search_wiki**: Full-text search across all wiki pages
   - `query` (required): Text to search for
   - `case_sensitive` (optional): Enable case-sensitive search (default: false)

2. **read_page**: Read complete page content
   - `page_name` (required): Page name (e.g., `Main.HomePage`)

3. **list_pages**: List all available wiki pages
   - `group` (optional): Filter by wiki group

## Environment Variables

- `WIKI_DIR`: Path to PmWiki's wiki.d directory (default: `/wiki_data`)

## Technical Stack

- **Language**: Python 3.11
- **Framework**: Starlette + Uvicorn
- **Protocol**: MCP over SSE
- **Port**: 3000

## Security

- The wiki directory is mounted read-only (`:ro`) by default
- No write operations are supported
- Safe for production wikis

## Verification

```bash
# Check server logs
docker logs pmwiki-mcp-server

# Test SSE connection
curl -N http://localhost:3000/sse
```

## Source Code

- GitHub: https://github.com/kcofoni/pmwiki-mcp
- Issues: https://github.com/kcofoni/pmwiki-mcp/issues
- Documentation: https://github.com/kcofoni/pmwiki-mcp#readme

## License

MIT License - See [LICENSE](https://github.com/kcofoni/pmwiki-mcp/blob/main/LICENSE) for details

---

**Note**: This server provides read-only access to your PmWiki content. It does not modify or write to your wiki files.
