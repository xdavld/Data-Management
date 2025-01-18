FROM selenium/standalone-chrome:latest

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip wget unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.83/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /usr/bin/ && \
    rm chrome-linux64.zip

RUN pip3 install --no-cache-dir selenium pandas --break-system-packages

ENV XDG_CACHE_HOME=/tmp/.cache
RUN mkdir -p /tmp/.cache && chmod -R 777 /tmp/.cache

WORKDIR /app

COPY src /app/src

RUN chmod +x /app/src/scrape_glasdoor.py
