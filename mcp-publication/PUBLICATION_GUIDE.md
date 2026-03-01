# MCP Server Publication Guide

This guide explains how to publish the PmWiki MCP server to the official MCP registry from the command line using the `mcp-publisher` tool.

## Prerequisites

Before publishing, ensure you have:

1. **mcp-publisher**: The official MCP publication tool
   ```bash
   # Download and install the binary
   curl -L "https://github.com/modelcontextprotocol/registry/releases/download/v1.4.0/mcp-publisher_linux_amd64.tar.gz" | tar xz && sudo mv mcp-publisher /usr/local/bin/.
   ```

2. **GitHub Account**: You need a GitHub account for namespace authentication (e.g., `io.github.username/*`)
3. **Docker and Docker Hub**: To build and publish the Docker image
4. **Updated server.json**: The `server.json` file must be properly configured

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

### Step 2: Build and Publish Docker Image

The MCP registry requires Docker images to support the `linux/amd64` architecture. The build method depends on your platform:

#### Option A: Simple Build (Linux AMD64, Debian, Ubuntu, etc.)

If building from an AMD64 Linux machine (Debian 12, Ubuntu, etc.), a simple build works:

```bash
# Build the image
docker build -t kcofoni/pmwiki-mcp:v1.0.3 -t kcofoni/pmwiki-mcp:latest .

# Push to Docker Hub
docker push kcofoni/pmwiki-mcp:v1.0.3
docker push kcofoni/pmwiki-mcp:latest
```

#### Option B: Multi-Architecture Build (Mac, Windows, or for ARM64 Support)

If building from a Mac (ARM64) or wanting to support multiple architectures:

```bash
# 1. Create and use a multi-architecture builder (one-time setup)
docker buildx create --use --name multiarch

# 2. Build and push for linux/amd64 and linux/arm64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t kcofoni/pmwiki-mcp:v1.0.3 \
  -t kcofoni/pmwiki-mcp:latest \
  --push \
  .
```

**Note**: The buildx `--push` flag directly uploads to Docker Hub. Multi-architecture images cannot be loaded locally.

**⚠️ Warning**: Building from a Mac without buildx creates ARM64-only images, causing publication errors (see Troubleshooting).

### Step 3: Authenticate with mcp-publisher

Before publishing, you need to authenticate with the MCP registry:

```bash
# Navigate to the directory containing server.json
cd mcp-publication/pmwiki

# Authenticate via GitHub OAuth
mcp-publisher login github
```

Follow the GitHub OAuth authentication flow. This allows you to publish to your `io.github.username/*` namespace.

### Step 4: Publish with mcp-publisher

Once authenticated, publish your server:

```bash
# Submit your server to the registry
mcp-publisher publish
```

The `mcp-publisher` tool will:
1. ✅ Validate your `server.json` against the official schema
2. ✅ Authenticate your namespace ownership (e.g., verify you own the GitHub account)
3. ✅ Submit your server metadata directly to the registry API
4. ✅ The registry will verify that the Docker image exists and is accessible

**Note**: Unlike Git-based workflows, `mcp-publisher` submits directly to the registry via API. It does **not** create forks, branches, commits, or pull requests. The submission is processed immediately by the registry.

### Step 5: Verify Publication

After successful publication:

```bash
# You'll see output like:
# ✓ Successfully published io.github.kcofoni/pmwiki-mcp@1.0.2
```

Your server will be available in the registry at:
- **Registry**: https://registry.modelcontextprotocol.io
- **Search**: Users can find your server by searching for "pmwiki"

### Advanced Options

#### Logout

To clear your authentication:

```bash
mcp-publisher logout github
```

## Updating an Existing Publication

When you release a new version:

1. Update [`mcp-publication/pmwiki/server.json`](./pmwiki/server.json) with the new version
2. Build and push the new Docker image (Option A or B depending on your platform, see Step 2)
3. Simply rerun `mcp-publisher publish` - the tool will automatically detect and update your existing registry entry

## Troubleshooting

### Publication Fails with Validation Errors

Common reasons for validation failures:
- **Invalid JSON**: Validate with `jq . server.json`
- **Missing Docker Image**: Ensure the image exists on Docker Hub
- **Incorrect Schema**: Check against the JSON schema specified in `$schema`
- **Incomplete Information**: Ensure all required fields are filled
- **Namespace Authentication**: Verify you're authenticated with the correct GitHub account for your namespace

### Docker Image Not Found

If the registry can't find your Docker image:
```bash
# Verify the image exists publicly
docker pull kcofoni/pmwiki-mcp:v1.0.2

# Check it's not private on Docker Hub
```

### Error "no child with platform linux/amd64"

If you get this error:
```
Error: publish failed: server returned status 400: {"title":"Bad Request","status":400,"detail":"Failed to publish server","errors":[{"message":"registry validation failed for package 0: no child with platform linux/amd64 in index"}]}
```

**Cause**: Your Docker image doesn't support the `linux/amd64` architecture (required by the MCP registry). This occurs when building from a Mac (ARM64) with a simple `docker build`.

**Solutions**:
1. **On Mac**: Use Docker Buildx (Option B in Step 2)
2. **Alternative**: Build from an AMD64 Linux machine (Debian, Ubuntu, etc.) using simple `docker build` (Option A in Step 2)

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
