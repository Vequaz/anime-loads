FROM python:3.13-slim

# Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Systempakete installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libgl1-mesa-glx \
    libxt6 \
    wget \
    git \
    gcc \
    lbzip2 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Geckodriver installieren
RUN wget -nv https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz \
 && tar -xf geckodriver-v0.36.0-linux64.tar.gz \
 && mv geckodriver /usr/local/bin/geckodriver \
 && chmod +x /usr/local/bin/geckodriver \
 && ln -s /usr/local/bin/geckodriver /usr/bin/geckodriver \
 && rm geckodriver-v0.36.0-linux64.tar.gz

# Python-Abhängigkeiten installieren
COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektcode kopieren
COPY anime-loads/ ./anime-loads/

# Arbeitsverzeichnis setzen
WORKDIR /usr/src/app/anime-loads

# Startbefehl (z. B. für Unraid mit externem Config-Verzeichnis)
ENTRYPOINT ["python", "anibot.py", "--configfile", "/config/ani.json"]
CMD ["--docker"]
