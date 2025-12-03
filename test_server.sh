#!/bin/bash

echo "=== Test du serveur MCP PmWiki ==="
echo

echo "1. Vérification du conteneur..."
docker ps | grep pmwiki-mcp-server
if [ $? -ne 0 ]; then
    echo "❌ Le conteneur n'est pas en cours d'exécution"
    exit 1
fi
echo "✅ Conteneur actif"
echo

echo "2. Test de l'endpoint SSE..."
timeout 2 curl -s -N http://localhost:3000/sse > /dev/null 2>&1
if [ $? -eq 124 ]; then
    echo "✅ Endpoint SSE répond"
else
    echo "❌ Endpoint SSE ne répond pas correctement"
fi
echo

echo "3. Vérification des logs..."
docker logs pmwiki-mcp-server 2>&1 | tail -5
echo

echo "4. Vérification du répertoire wiki..."
docker exec pmwiki-mcp-server ls -la /wiki_data | head -10
echo

echo "=== Test terminé ==="
