# MCP Server Publication Guide

This guide explains how to publish the PmWiki MCP server to the official MCP registry from the command line using the `mcp-publisher` tool.

## Prerequisites

Before publishing, ensure you have:

1. **mcp-publisher**: The official MCP publication tool
   ```bash
   # Download and install the binary
   curl -L "https://github.com/modelcontextprotocol/registry/releases/download/v1.4.0/mcp-publisher_linux_amd64.tar.gz" | tar xz && sudo mv mcp-publisher /usr/local/bin/.
   ```

2. **GitHub Account**: You need a GitHub account with access to the repository
3. **GitHub CLI (`gh`)**: Install it from https://cli.github.com/
4. **Docker and Docker Hub**: To build and publish the image
5. **Updated server.json**: The `server.json` file must be properly configured

## Quick Installation of mcp-publisher

If `mcp-publisher` is not yet installed on your system:

### Linux (amd64)

```bash
# Download and install the binary from GitHub
curl -L "https://github.com/modelcontextprotocol/registry/releases/download/v1.4.0/mcp-publisher_linux_amd64.tar.gz" | tar xz && sudo mv mcp-publisher /usr/local/bin/.

# Verify installation
mcp-publisher --version
```

This method directly installs the precompiled binary without requiring Node.js.

### Other Platforms

For macOS, Windows, or other architectures, check the [releases page](https://github.com/modelcontextprotocol/registry/releases) for the appropriate binary.

## Publication Process

### Step 1: Verify Your Configuration

Check that [`mcp-publication/pmwiki/server.json`](./pmwiki/server.json) is correctly configured:

```bash
cat mcp-publication/pmwiki/server.json
```

Key fields to verify:
- `name`: Should be `io.github.kcofoni/pmwiki-mcp`
- `version`: Must match your Docker image tag (e.g., `1.0.2`)
- `repository.url`: Your GitHub repository URL
- `packages[0].identifier`: Docker image with correct version tag

### Step 2: Ensure Docker Image is Published

Before submitting to the MCP registry, verify your Docker image is available on Docker Hub:

```bash
# Build the Docker image
docker build -t kcofoni/pmwiki-mcp:v1.0.2 .

# Tag as latest
docker tag kcofoni/pmwiki-mcp:v1.0.2 kcofoni/pmwiki-mcp:latest

# Push to Docker Hub
docker push kcofoni/pmwiki-mcp:v1.0.2
docker push kcofoni/pmwiki-mcp:latest
```

### Step 3: Publish with mcp-publisher

The `mcp-publisher` tool greatly simplifies the publication process. From the project root directory:

```bash
# Navigate to the directory containing server.json
cd mcp-publication/pmwiki

# Launch the interactive publication
mcp-publisher publish
```

The `mcp-publisher` tool will:
1. ✅ Validate your `server.json` against the official schema
2. ✅ Verify that the Docker image exists and is accessible
3. ✅ Automatically fork the MCP registry if needed
4. ✅ Create a branch with an appropriate name
5. ✅ Copy your `server.json` to the correct location
6. ✅ Create a commit with an appropriate message
7. ✅ Push changes to your fork
8. ✅ Automatically create the Pull Request

### Step 4: Advanced Options with mcp-publisher

#### Non-Interactive Publication

To automate the publication (for CI/CD for example):

```bash
mcp-publisher publish \
  --server-json ./server.json \
  --non-interactive
```

#### Updating an Existing Publication

To update an already published server:

```bash
# First update the version in server.json
# Then republish
mcp-publisher publish
```

The tool will automatically detect that this is an update.

### Step 5: Monitor the Pull Request

After `mcp-publisher` has created the PR:

1. Watch for feedback from the MCP registry maintainers
2. Respond to any requested changes
3. If changes are needed:
   ```bash
   # Modify server.json based on feedback
   # Then rerun publication (this will update the existing PR)
   mcp-publisher publish
   ```

## Updating an Existing Publication

When you release a new version:

1. Update [`mcp-publication/pmwiki/server.json`](./pmwiki/server.json) with the new version
2. Build and push the new Docker image
3. Simply rerun `mcp-publisher publish` - the tool will automatically handle the update

## Troubleshooting

### PR Gets Rejected

Common reasons for rejection:
- **Invalid JSON**: Validate with `jq . server.json`
- **Missing Docker Image**: Ensure the image exists on Docker Hub
- **Incorrect Schema**: Check against the JSON schema specified in `$schema`
- **Incomplete Information**: Ensure all required fields are filled

### Docker Image Not Found

If the registry can't find your Docker image:
```bash
# Verify the image exists publicly
docker pull kcofoni/pmwiki-mcp:v1.0.2

# Check it's not private on Docker Hub
```

### Schema Validation Errors

Validate your server.json against the schema:
```bash
# Using a JSON schema validator
curl -o schema.json https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json
# Use an online validator or a CLI tool to validate
```

## Resources

- **MCP Registry**: https://github.com/modelcontextprotocol/registry
- **MCP Documentation**: https://modelcontextprotocol.io/
- **Server Schema**: https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json
- **PmWiki MCP Repository**: https://github.com/kcofoni/pmwiki-mcp

## Support

For issues specific to this server, please open an issue on the [PmWiki MCP repository](https://github.com/kcofoni/pmwiki-mcp/issues).
