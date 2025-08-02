# Utiliser Python 3.11 slim pour réduire la taille
FROM python:3.11-slim

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Créer l'utilisateur non-root
RUN groupadd -r zukii && useradd -r -g zukii zukii

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs && \
    chown -R zukii:zukii /app

# Copier le code source
COPY . .

# Changer les permissions
RUN chown -R zukii:zukii /app

# Passer à l'utilisateur non-root
USER zukii

# Exposer le port
EXPOSE 8000

# Point d'entrée
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]