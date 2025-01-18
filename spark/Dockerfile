FROM bitnami/spark:3.4.1

USER root

# Install necessary packages
RUN apt-get update && \
    apt-get install -y curl python3-pip openjdk-11-jdk && \
    mkdir -p /opt/spark/jars && \
    # Install Delta Lake package
    curl -L https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar -o /opt/spark/jars/delta-core_2.12-2.4.0.jar && \
    # Install Hadoop AWS and AWS SDK
    curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.0/hadoop-aws-3.4.0.jar -o /opt/spark/jars/hadoop-aws-3.4.0.jar && \
    curl -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.277/aws-java-sdk-bundle-1.12.277.jar -o /opt/spark/jars/aws-java-sdk-bundle-1.12.277.jar && \
    # Install Python dependencies
    pip3 install delta-spark==2.4.0 boto3 pandas pyarrow duckdb ibis-framework s3fs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

    WORKDIR /app

    CMD ["python", "src/main.py"]

USER 1001
