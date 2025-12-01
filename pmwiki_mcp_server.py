# pmwiki_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource
import mcp.types as types
import os
import re
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer le serveur MCP
mcp_server = Server("pmwiki-server")

# Le répertoire sera monté depuis le volume Docker
WIKI_DIR = os.getenv("WIKI_DIR", "/wiki_data")


def parse_pmwiki_file(filepath):
    """Parse un fichier PmWiki et extrait le contenu"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extraire le texte après "text="
        match = re.search(r"text=(.+?)(?:\n[a-z]+=|$)", content, re.DOTALL)
        if match:
            text = match.group(1)
            # Décoder le format PmWiki
            text = text.replace("%0a", "\n")
            text = text.replace("%25", "%")
            text = text.replace("%22", '"')
            text = text.replace("%3c", "<")
            text = text.replace("%3e", ">")
            return text
        return ""
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {filepath}: {str(e)}")
        return f"Erreur lors de la lecture: {str(e)}"


def get_page_title(filename):
    """Extrait le titre de la page depuis le nom de fichier"""
    return filename.replace(".", "/")


@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """Liste toutes les pages du wiki comme ressources"""
    resources = []

    if not os.path.exists(WIKI_DIR):
        logger.warning(f"Le répertoire {WIKI_DIR} n'existe pas")
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
                        description=f"Page wiki: {get_page_title(filename)}",
                    )
                )

        logger.info(f"Trouvé {len(resources)} pages wiki")
    except Exception as e:
        logger.error(f"Erreur lors du listing des ressources: {str(e)}")

    return resources


@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Lit le contenu d'une page wiki"""
    if not uri.startswith("pmwiki://"):
        raise ValueError("URI invalide")

    filename = uri.replace("pmwiki://", "")
    filepath = os.path.join(WIKI_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Page {filename} introuvable")

    content = parse_pmwiki_file(filepath)
    return content


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Liste les outils disponibles"""
    return [
        Tool(
            name="search_wiki",
            description="Recherche du texte dans toutes les pages du wiki PmWiki. Retourne les pages contenant le texte recherché avec un extrait du contexte.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texte à rechercher dans le wiki",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Recherche sensible à la casse (par défaut: false)",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="read_page",
            description="Lit le contenu complet d'une page wiki spécifique. Utilisez le format 'Group.PageName' ou 'Group/PageName'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_name": {
                        "type": "string",
                        "description": "Nom de la page (ex: Main.HomePage ou Main/HomePage)",
                    }
                },
                "required": ["page_name"],
            },
        ),
        Tool(
            name="list_pages",
            description="Liste toutes les pages disponibles dans le wiki, optionnellement filtrées par groupe.",
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {
                        "type": "string",
                        "description": "Nom du groupe pour filtrer les pages (optionnel)",
                    }
                },
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Exécute un outil"""

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
                    text=f"Erreur: Le répertoire wiki {WIKI_DIR} n'existe pas",
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
                # Trouver le contexte autour de la première occurrence
                index = search_content.find(query)
                start = max(0, index - 100)
                end = min(len(content), index + 100)
                snippet = content[start:end].strip()

                results.append(
                    {"page": get_page_title(filename), "snippet": f"...{snippet}..."}
                )

        if not results:
            return [
                TextContent(type="text", text=f"Aucun résultat trouvé pour '{query}'")
            ]

        result_text = f"Trouvé {len(results)} résultat(s) pour '{query}':\n\n"
        for r in results[:10]:  # Limiter à 10 résultats
            result_text += f"**{r['page']}**\n{r['snippet']}\n\n"

        if len(results) > 10:
            result_text += f"\n... et {len(results) - 10} autres résultats"

        return [TextContent(type="text", text=result_text)]

    elif name == "read_page":
        page_name = arguments["page_name"]
        # Convertir Main/HomePage en Main.HomePage
        filename = page_name.replace("/", ".")
        filepath = os.path.join(WIKI_DIR, filename)

        if not os.path.exists(filepath):
            # Essayer de lister les pages similaires
            similar = []
            search_term = page_name.lower().replace("/", ".").replace(".", "")

            for fname in os.listdir(WIKI_DIR):
                if search_term in fname.lower().replace(".", ""):
                    similar.append(get_page_title(fname))

            suggestion = ""
            if similar:
                suggestion = f"\n\nPages similaires trouvées:\n" + "\n".join(
                    [f"- {p}" for p in similar[:5]]
                )

            return [
                TextContent(
                    type="text",
                    text=f"Page '{page_name}' introuvable.{suggestion}\n\nUtilisez 'list_pages' pour voir toutes les pages disponibles.",
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
                    text=f"Erreur: Le répertoire wiki {WIKI_DIR} n'existe pas",
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
            msg = "Aucune page trouvée"
            if group_filter:
                msg += f" dans le groupe '{group_filter}'"
            return [TextContent(type="text", text=msg)]

        # Grouper les pages par groupe
        grouped = {}
        for page in pages:
            if "/" in page:
                group = page.split("/")[0]
            else:
                group = "Racine"

            if group not in grouped:
                grouped[group] = []
            grouped[group].append(page)

        result_text = f"Pages disponibles ({len(pages)}):\n\n"
        for group, group_pages in sorted(grouped.items()):
            result_text += f"**{group}** ({len(group_pages)} pages)\n"
            for page in group_pages[:10]:  # Limiter l'affichage
                result_text += f"  - {page}\n"
            if len(group_pages) > 10:
                result_text += f"  ... et {len(group_pages) - 10} autres pages\n"
            result_text += "\n"

        return [TextContent(type="text", text=result_text)]

    else:
        return [TextContent(type="text", text=f"Outil inconnu: {name}")]


# Point d'entrée pour SSE
async def run_sse_server():
    """Démarre le serveur en mode SSE"""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    import uvicorn

    async def handle_sse(request):
        async with SseServerTransport("/messages") as transport:
            await mcp_server.run(
                transport.read_stream,
                transport.write_stream,
                mcp_server.create_initialization_options(),
            )
        return transport.get_response()

    async def handle_messages(request):
        return {"status": "ok"}

    app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ],
    )

    config = uvicorn.Config(app, host="0.0.0.0", port=3000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    import asyncio

    logger.info(f"Démarrage du serveur MCP PmWiki sur le port 3000")
    logger.info(f"Répertoire wiki: {WIKI_DIR}")

    asyncio.run(run_sse_server())
