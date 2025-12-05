#!/bin/bash

echo "=== PmWiki MCP Server Test ==="
echo

echo "1. Checking container..."
docker ps | grep pmwiki-mcp-server
if [ $? -ne 0 ]; then
    echo "❌ Container is not running"
    exit 1
fi
echo "✅ Container active"
echo

echo "2. Testing SSE endpoint..."
timeout 2 curl -s -N http://localhost:3000/sse > /dev/null 2>&1
if [ $? -eq 124 ]; then
    echo "✅ SSE endpoint responding"
else
    echo "❌ SSE endpoint not responding correctly"
fi
echo

echo "3. Checking logs..."
docker logs pmwiki-mcp-server 2>&1 | tail -5
echo

echo "4. Checking wiki directory..."
docker exec pmwiki-mcp-server ls -la /wiki_data | head -10
echo

echo "=== Test completed ==="
