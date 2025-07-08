FROM python:3.13-slim

# Set UTF-8 locale
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set working directory
WORKDIR /usr/src/app

# Install OS dependencies including Firefox ESR
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    curl \
    firefox-esr \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libgl1-mesa-glx \
    lbzip2 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Clone the anime-loads repository
RUN git clone https://github.com/vequaz/anime-loads.git

# Set working directory to the project folder
WORKDIR /usr/src/app/anime-loads

# Install Geckodriver (linux64)
ENV GECKODRIVER_VERSION=v0.36.0
RUN wget -nv "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" \
 && tar -xf "geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" \
 && mv geckodriver /usr/bin/geckodriver \
 && chmod +x /usr/bin/geckodriver \
 && rm "geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Unraid-compatible config volume
VOLUME ["/config"]

# Entrypoint and default CMD
ENTRYPOINT ["python", "anibot.py", "--configfile", "/config/ani.json"]
CMD ["--docker"]
