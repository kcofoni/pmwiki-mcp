# PmWiki MCP Server

MCP (Model Context Protocol) server for interfacing an LLM with PmWiki.

[Version française / French version](README_fr.md)

## Architecture

The server uses the MCP protocol with SSE (Server-Sent Events) transport to enable an LLM to interact with your PmWiki instance.

### Endpoints

- `GET /sse`: SSE connection to establish bidirectional communication
- `POST /messages/`: Receive messages from the MCP client

## Getting Started

### With Docker Compose (Docker Hub image)

The simplest method is to use the published image from Docker Hub:

```bash
docker compose up -d
```

### With Docker Compose (local build)

If you want to build the image locally:

1. Edit `docker-compose.yml` and comment out the `image:` line, then uncomment the `build: .` line
2. Run:

```bash
docker compose up -d --build
```

### Direct Docker Usage

Without docker-compose, you can run directly:

```bash
docker run -d \
  --name pmwiki-mcp-server \
  -p 3000:3000 \
  -v /path/to/your/wiki.d:/wiki_data:ro \
  -e WIKI_DIR=/wiki_data \
  kcofoni/pmwiki-mcp:latest
```

The server will be accessible at `http://localhost:3000` (or `http://vmtest:3000` from other machines on the network).

### Verification

```bash
# Check that the server is running
docker logs pmwiki-mcp-server

# Test the SSE connection
curl -N http://localhost:3000/sse
```

## Client Configuration

### Claude Desktop

Add this configuration to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pmwiki": {
      "command": "mcp-proxy",
      "args": [
        "--transport=sse",
        "http://vmtest:3000/sse"
      ]
    }
  }
}
```

**Important notes**:
- `vmtest` is the hostname of the machine hosting the MCP server Docker container
- Replace `vmtest` with:
  - `localhost` if Claude Desktop runs on the same machine as the server
  - The hostname or IP address of the machine running the Docker container (e.g., `192.168.1.100:3000/sse`)
- The `mcp-proxy` tool must be installed (usually provided with Claude Desktop)
- The proxy handles the SSE connection between Claude Desktop and the MCP server

## Available Features

Once connected, your LLM will have access to:

### Resources

- All wiki pages are exposed as resources with the URI `pmwiki://Group.PageName`

### Tools

1. **search_wiki**: Search for text across all pages
   - Parameters:
     - `query` (required): Text to search for
     - `case_sensitive` (optional): Case-sensitive search (default: false)

2. **read_page**: Read the complete content of a page
   - Parameters:
     - `page_name` (required): Page name (e.g., `Main.HomePage` or `Main/HomePage`)

3. **list_pages**: List all wiki pages
   - Parameters:
     - `group` (optional): Filter by group

## Configuration

### Wiki Directory Mount

The PmWiki directory is mounted from the host machine to the Docker container:

```yaml
volumes:
  - /home/docker/appdata/html/wiki.d:/wiki_data:ro
```

**Important**:
- `/home/docker/appdata/html/wiki.d` is the path **on the host machine** - this is an example to adapt
- Replace this path with the actual path to your PmWiki `wiki.d` directory
- The volume is mounted read-only (`:ro`) for security reasons
- `/wiki_data` is the internal container path (do not modify)

## Docker Hub

The image is publicly available on Docker Hub:
- **Repository**: [kcofoni/pmwiki-mcp](https://hub.docker.com/r/kcofoni/pmwiki-mcp)
- **Latest tag**: `kcofoni/pmwiki-mcp:latest`
- **Stable version**: `kcofoni/pmwiki-mcp:v1.0.1`

To pull the latest version:
```bash
docker pull kcofoni/pmwiki-mcp:latest
```

To pull a specific version:
```bash
docker pull kcofoni/pmwiki-mcp:v1.0.1
```

## Technical Architecture

- **Language**: Python 3.11
- **Web Framework**: Starlette + Uvicorn
- **Protocol**: MCP over SSE
- **Page Format**: PmWiki (files in `wiki.d/`)

## Logs

```bash
# View logs in real-time
docker logs -f pmwiki-mcp-server

# Last 50 lines
docker logs --tail 50 pmwiki-mcp-server
```

## Troubleshooting

### Server won't start

Check that the wiki directory exists:
```bash
ls -la /home/docker/appdata/html/wiki.d
```

### 404 error on a page

Use the `list_pages` tool to see all available pages. The exact PmWiki filename format must be used (e.g., `Main.HomePage` not `Main/HomePage` for the file).

### SSE connection fails

Check that port 3000 is properly exposed:
```bash
docker ps | grep pmwiki-mcp-server
```

## Development

### File Structure

```
pmwiki-mcp/
├── pmwiki_mcp_server.py    # MCP server
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose configuration
├── README.md              # This documentation (English)
└── README_fr.md           # French documentation
```

### Code Modification

After modifying the code:
```bash
docker compose up -d --build
```
