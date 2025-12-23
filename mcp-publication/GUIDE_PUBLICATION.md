# Guide de Publication du Serveur MCP

Ce guide explique comment publier le serveur MCP PmWiki sur le registre officiel MCP en ligne de commande en utilisant l'outil `mcp-publisher`.

## Prérequis

Avant de publier, assurez-vous d'avoir :

1. **mcp-publisher** : L'outil officiel de publication MCP
   ```bash
   # Télécharger et installer le binaire
   curl -L "https://github.com/modelcontextprotocol/registry/releases/download/v1.4.0/mcp-publisher_linux_amd64.tar.gz" | tar xz && sudo mv mcp-publisher /usr/local/bin/.
   ```

2. **Compte GitHub** : Vous devez avoir un compte GitHub pour l'authentification de l'espace de noms (ex: `io.github.nomutilisateur/*`)
3. **Docker et Docker Hub** : Pour construire et publier l'image Docker
4. **server.json à jour** : Le fichier `server.json` doit être correctement configuré

## Installation Rapide de mcp-publisher

Si `mcp-publisher` n'est pas encore installé sur votre système :

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

### Étape 3 : S'authentifier avec mcp-publisher

Avant de publier, vous devez vous authentifier auprès du registre MCP :

```bash
# Se placer dans le répertoire contenant server.json
cd mcp-publication/pmwiki

# S'authentifier (OAuth GitHub ou DNS)
mcp-publisher login
```

Suivez le processus d'authentification. Pour les espaces de noms basés sur GitHub (comme `io.github.nomutilisateur/*`), vous vous authentifierez via OAuth GitHub.

### Étape 4 : Publier avec mcp-publisher

Une fois authentifié, publiez votre serveur :

```bash
# Soumettre votre serveur au registre
mcp-publisher publish
```

L'outil `mcp-publisher` va :
1. ✅ Valider votre fichier `server.json` selon le schéma officiel
2. ✅ Authentifier la propriété de votre espace de noms (ex: vérifier que vous possédez le compte GitHub)
3. ✅ Soumettre les métadonnées de votre serveur directement à l'API du registre
4. ✅ Le registre vérifiera que l'image Docker existe et est accessible

**Note** : Contrairement aux workflows basés sur Git, `mcp-publisher` soumet directement au registre via API. Il ne crée **pas** de forks, branches, commits ou pull requests. La soumission est traitée immédiatement par le registre.

### Étape 5 : Vérifier la Publication

Après une publication réussie :

```bash
# Vous verrez un message du type :
# ✓ Successfully published io.github.kcofoni/pmwiki-mcp@1.0.2
```

Votre serveur sera disponible dans le registre à :
- **Registre** : https://registry.modelcontextprotocol.io
- **Recherche** : Les utilisateurs peuvent trouver votre serveur en recherchant "pmwiki"

### Options Avancées

#### Déconnexion

Pour effacer votre authentification :

```bash
mcp-publisher logout
```

## Mise à Jour d'une Publication Existante

Lorsque vous publiez une nouvelle version :

1. Mettez à jour [`mcp-publication/pmwiki/server.json`](./pmwiki/server.json) avec la nouvelle version
2. Construisez et poussez la nouvelle image Docker
3. Relancez simplement `mcp-publisher publish` - l'outil détectera automatiquement et mettra à jour votre entrée dans le registre

## Dépannage

### La Publication Échoue avec des Erreurs de Validation

Raisons courantes d'échec de validation :
- **JSON Invalide** : Validez avec `jq . server.json`
- **Image Docker Manquante** : Assurez-vous que l'image existe sur Docker Hub
- **Schéma Incorrect** : Vérifiez par rapport au schéma JSON spécifié dans `$schema`
- **Informations Incomplètes** : Assurez-vous que tous les champs requis sont remplis
- **Authentification de l'Espace de Noms** : Vérifiez que vous êtes authentifié avec le bon compte GitHub pour votre espace de noms

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
