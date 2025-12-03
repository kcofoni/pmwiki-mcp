FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le serveur
COPY pmwiki_mcp_server.py .

# Exposer le port SSE
EXPOSE 3000

CMD ["python", "-u", "pmwiki_mcp_server.py"]