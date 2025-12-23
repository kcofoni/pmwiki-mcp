# Guide de Publication du Serveur MCP

Ce guide explique comment publier le serveur MCP PmWiki sur le registre officiel MCP en ligne de commande en utilisant l'outil `mcp-publisher`.

## Prérequis

Avant de publier, assurez-vous d'avoir :

1. **mcp-publisher** : L'outil officiel de publication MCP
   ```bash
   # Télécharger et installer le binaire
   curl -L "https://github.com/modelcontextprotocol/registry/releases/download/v1.4.0/mcp-publisher_linux_amd64.tar.gz" | tar xz && sudo mv mcp-publisher /usr/local/bin/.
   ```

2. **Compte GitHub** : Vous devez avoir un compte GitHub avec accès au dépôt
3. **GitHub CLI (`gh`)** : Installez-le depuis https://cli.github.com/
4. **Docker et Docker Hub** : Pour construire et publier l'image
5. **server.json à jour** : Le fichier `server.json` doit être correctement configuré

## Installation Rapide de mcp-publisher

Si `mcp-publisher` n'est pas encore installé sur votre système Debian 12 :

```bash
# Télécharger et installer le binaire depuis GitHub
curl -L "https://github.com/modelcontextprotocol/registry/releases/download/v1.4.0/mcp-publisher_linux_amd64.tar.gz" | tar xz && sudo mv mcp-publisher /usr/local/bin/.

# Vérifier l'installation
mcp-publisher --version
```

Cette méthode installe directement le binaire précompilé sans nécessiter Node.js.

## Processus de Publication

### Étape 1 : Vérifier Votre Configuration

Vérifiez que [`mcp-publication/pmwiki/server.json`](./pmwiki/server.json) est correctement configuré :

```bash
cat mcp-publication/pmwiki/server.json
```

Champs clés à vérifier :
- `name` : Doit être `io.github.kcofoni/pmwiki-mcp`
- `version` : Doit correspondre au tag de votre image Docker (ex: `1.0.2`)
- `repository.url` : L'URL de votre dépôt GitHub
- `packages[0].identifier` : Image Docker avec le bon tag de version

### Étape 2 : S'assurer que l'Image Docker est Publiée

Avant de soumettre au registre MCP, vérifiez que votre image Docker est disponible sur Docker Hub :

```bash
# Construire l'image Docker
docker build -t kcofoni/pmwiki-mcp:v1.0.2 .

# Taguer comme latest
docker tag kcofoni/pmwiki-mcp:v1.0.2 kcofoni/pmwiki-mcp:latest

# Pousser sur Docker Hub
docker push kcofoni/pmwiki-mcp:v1.0.2
docker push kcofoni/pmwiki-mcp:latest
```

### Étape 3 : Publier avec mcp-publisher

L'outil `mcp-publisher` simplifie grandement le processus de publication. Depuis le répertoire racine du projet :

```bash
# Se placer dans le répertoire contenant server.json
cd mcp-publication/pmwiki

# Lancer la publication interactive
mcp-publisher publish
```

L'outil `mcp-publisher` va :
1. ✅ Valider votre fichier `server.json` selon le schéma officiel
2. ✅ Vérifier que l'image Docker existe et est accessible
3. ✅ Forker automatiquement le registre MCP si nécessaire
4. ✅ Créer une branche avec un nom approprié
5. ✅ Copier votre `server.json` au bon emplacement
6. ✅ Créer un commit avec un message approprié
7. ✅ Pousser les changements sur votre fork
8. ✅ Créer automatiquement la Pull Request

### Étape 4 : Options Avancées avec mcp-publisher

#### Publication Non-Interactive

Pour automatiser la publication (CI/CD par exemple) :

```bash
mcp-publisher publish \
  --server-json ./server.json \
  --non-interactive
```

#### Mise à Jour d'une Publication Existante

Pour mettre à jour un serveur déjà publié :

```bash
# Mettez d'abord à jour la version dans server.json
# Puis republier
mcp-publisher publish
```

L'outil détectera automatiquement qu'il s'agit d'une mise à jour.

### Étape 5 : Suivre la Pull Request

Après que `mcp-publisher` ait créé la PR :

1. Surveillez les retours des mainteneurs du registre MCP
2. Répondez aux modifications demandées
3. Si des changements sont nécessaires :
   ```bash
   # Modifier server.json selon les retours
   # Puis relancer la publication (cela mettra à jour la PR existante)
   mcp-publisher publish
   ```

## Mise à Jour d'une Publication Existante

Lorsque vous publiez une nouvelle version :

1. Mettez à jour [`mcp-publication/pmwiki/server.json`](./pmwiki/server.json) avec la nouvelle version
2. Construisez et poussez la nouvelle image Docker
3. Relancez simplement `mcp-publisher publish` - l'outil gèrera automatiquement la mise à jour

## Dépannage

### La PR est Rejetée

Raisons courantes de rejet :
- **JSON Invalide** : Validez avec `jq . server.json`
- **Image Docker Manquante** : Assurez-vous que l'image existe sur Docker Hub
- **Schéma Incorrect** : Vérifiez par rapport au schéma JSON spécifié dans `$schema`
- **Informations Incomplètes** : Assurez-vous que tous les champs requis sont remplis

### Image Docker Introuvable

Si le registre ne trouve pas votre image Docker :
```bash
# Vérifier que l'image existe publiquement
docker pull kcofoni/pmwiki-mcp:v1.0.2

# Vérifier qu'elle n'est pas privée sur Docker Hub
```

### Erreurs de Validation du Schéma

Validez votre server.json par rapport au schéma :
```bash
# Utiliser un validateur de schéma JSON
curl -o schema.json https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json
# Utiliser un validateur en ligne ou un outil CLI pour valider
```

## Ressources

- **Registre MCP** : https://github.com/modelcontextprotocol/registry
- **Documentation MCP** : https://modelcontextprotocol.io/
- **Schéma du Serveur** : https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json
- **Dépôt PmWiki MCP** : https://github.com/kcofoni/pmwiki-mcp

## Support

Pour les problèmes spécifiques à ce serveur, veuillez ouvrir une issue sur le [dépôt PmWiki MCP](https://github.com/kcofoni/pmwiki-mcp/issues).
