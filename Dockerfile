FROM python:3.10-slim

# Installer Stockfish sur le serveur Linux de Render
RUN apt-get update && apt-get install -y stockfish && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

EXPOSE 5000

# Lancer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]