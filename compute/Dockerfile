# Stage 1: Base with OpenJDK
FROM openjdk:11-jdk-slim-bullseye AS base

# Install necessary utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip procps && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Verify Java installation
RUN java -version && \
    echo "JAVA_HOME is set to $JAVA_HOME" && \
    ls -la $JAVA_HOME/bin/java

# Stage 2: Application
FROM base AS app

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Define the command to run the application
CMD ["python3", "src/main.py"]
