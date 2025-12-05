# Serveur MCP PmWiki

Serveur MCP (Model Context Protocol) pour interfacer un LLM avec PmWiki.

## Architecture

Le serveur utilise le protocole MCP avec transport SSE (Server-Sent Events) pour permettre à un LLM d'interagir avec votre wiki PmWiki.

### Endpoints

- `GET /sse` : Connexion SSE pour établir la communication bidirectionnelle
- `POST /messages/` : Réception des messages du client MCP

## Démarrage

### Avec Docker Compose (image Docker Hub)

La méthode la plus simple est d'utiliser l'image publiée sur Docker Hub :

```bash
docker compose up -d
```

### Avec Docker Compose (build local)

Si vous souhaitez construire l'image localement :

1. Éditez `docker-compose.yml` et commentez la ligne `image:`, puis décommentez la ligne `build: .`
2. Lancez :

```bash
docker compose up -d --build
```

### Utilisation directe avec Docker

Sans docker-compose, vous pouvez aussi lancer directement :

```bash
docker run -d \
  --name pmwiki-mcp-server \
  -p 3000:3000 \
  -v /chemin/vers/votre/wiki.d:/wiki_data:ro \
  -e WIKI_DIR=/wiki_data \
  kcofoni/pmwiki-mcp:latest
```

Le serveur sera accessible sur `http://localhost:3000` (ou `http://vmtest:3000` depuis d'autres machines du réseau).

### Vérification

```bash
# Vérifier que le serveur fonctionne
docker logs pmwiki-mcp-server

# Tester la connexion SSE
curl -N http://localhost:3000/sse
```

## Configuration du client

### Claude Desktop

Ajoutez cette configuration à votre fichier de configuration Claude Desktop :

**Sur macOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
**Sur Windows** : `%APPDATA%\Claude\claude_desktop_config.json`

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

**Notes importantes** :
- `vmtest` est le nom de la machine qui héberge le conteneur Docker du serveur MCP
- Remplacez `vmtest` par :
  - `localhost` si Claude Desktop s'exécute sur la même machine que le serveur
  - Le nom d'hôte ou l'adresse IP de la machine qui exécute le conteneur Docker (ex: `192.168.1.100:3000/sse`)
- L'outil `mcp-proxy` doit être installé (il est généralement fourni avec Claude Desktop)
- Le proxy gère la connexion SSE entre Claude Desktop et le serveur MCP

## Fonctionnalités disponibles

Une fois connecté, votre LLM aura accès à :

### Ressources

- Toutes les pages du wiki sont exposées comme ressources avec l'URI `pmwiki://Group.PageName`

### Outils

1. **search_wiki** : Recherche du texte dans toutes les pages
   - Paramètres :
     - `query` (requis) : Texte à rechercher
     - `case_sensitive` (optionnel) : Recherche sensible à la casse (défaut: false)

2. **read_page** : Lit le contenu complet d'une page
   - Paramètres :
     - `page_name` (requis) : Nom de la page (ex: `Main.HomePage` ou `Main/HomePage`)

3. **list_pages** : Liste toutes les pages du wiki
   - Paramètres :
     - `group` (optionnel) : Filtre par groupe

## Configuration

### Montage du répertoire wiki

Le répertoire wiki de PmWiki est monté depuis la machine hôte vers le conteneur Docker :

```yaml
volumes:
  - /home/docker/appdata/html/wiki.d:/wiki_data:ro
```

**Important** :
- `/home/docker/appdata/html/wiki.d` est le chemin **sur la machine hôte** - c'est un exemple à adapter
- Remplacez ce chemin par le chemin réel vers votre répertoire `wiki.d` de PmWiki
- Le volume est monté en lecture seule (`:ro`) pour des raisons de sécurité
- `/wiki_data` est le chemin interne au conteneur (ne pas modifier)

## Docker Hub

L'image est disponible publiquement sur Docker Hub :
- **Repository** : [kcofoni/pmwiki-mcp](https://hub.docker.com/r/kcofoni/pmwiki-mcp)
- **Tag latest** : `kcofoni/pmwiki-mcp:latest`

Pour récupérer la dernière version :
```bash
docker pull kcofoni/pmwiki-mcp:latest
```

## Architecture technique

- **Langage** : Python 3.11
- **Framework web** : Starlette + Uvicorn
- **Protocole** : MCP over SSE
- **Format des pages** : PmWiki (fichiers dans `wiki.d/`)

## Logs

```bash
# Voir les logs en temps réel
docker logs -f pmwiki-mcp-server

# Dernières 50 lignes
docker logs --tail 50 pmwiki-mcp-server
```

## Dépannage

### Le serveur ne démarre pas

Vérifiez que le répertoire wiki existe :
```bash
ls -la /home/docker/appdata/html/wiki.d
```

### Erreur 404 sur une page

Utilisez l'outil `list_pages` pour voir toutes les pages disponibles. Le format exact du nom de fichier PmWiki doit être utilisé (ex: `Main.HomePage` et non `Main/HomePage` pour le fichier).

### Connexion SSE échoue

Vérifiez que le port 3000 est bien exposé :
```bash
docker ps | grep pmwiki-mcp-server
```

## Développement

### Structure des fichiers

```
pmwiki-mcp/
├── pmwiki_mcp_server.py    # Serveur MCP
├── requirements.txt         # Dépendances Python
├── Dockerfile              # Image Docker
├── docker-compose.yml      # Configuration Docker Compose
└── README.md              # Cette documentation
```

### Modification du code

Après modification du code :
```bash
docker compose up -d --build
```
