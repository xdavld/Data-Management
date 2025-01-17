import os
import sys
from pathlib import Path

from minio import Minio
from minio.error import S3Error
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

def load_environment_variables():
    """
    Load and validate necessary environment variables.
    """
    required_vars = [
        "MINIO_ENDPOINT",
        "MINIO_ACCESS_KEY",
        "MINIO_SECRET_KEY",
        "MINIO_BUCKET",
        "DATA_CSV_PATH",
        "SPARK_APP_NAME",
    ]

    env_vars = {}
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        else:
            env_vars[var] = value

    if missing_vars:
        sys.exit(f"Error: Missing environment variables: {', '.join(missing_vars)}")

    return env_vars

def initialize_minio_client(endpoint, access_key, secret_key):
    """
    Initialize and return a MinIO client.
    """
    try:
        client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # Set to True if using HTTPS
        )
        return client
    except Exception as e:
        sys.exit(f"Error initializing MinIO client: {e}")

def ensure_bucket_exists(client, bucket_name):
    """
    Check if the specified bucket exists; if not, create it.
    """
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as e:
        sys.exit(f"Error checking/creating bucket '{bucket_name}': {e}")

def configure_spark_session(app_name, delta_packages):
    """
    Configure and return a SparkSession with Delta Lake support.
    """
    try:
        builder = SparkSession.builder.appName(app_name) \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

        spark = configure_spark_with_delta_pip(builder, extra_packages=delta_packages).getOrCreate()
        return spark
    except Exception as e:
        sys.exit(f"Error configuring Spark session: {e}")

def set_spark_hadoop_conf(spark, confs):
    """
    Set Hadoop configurations for SparkContext.
    """
    try:
        sc = spark.sparkContext
        hadoop_conf = sc._jsc.hadoopConfiguration()
        for key, value in confs.items():
            hadoop_conf.set(key, value)
        print("Spark Hadoop configurations set.")
    except Exception as e:
        sys.exit(f"Error setting Spark Hadoop configurations: {e}")

def load_and_write_data(spark, csv_path, bucket_name, output_path, partition_column):
    """
    Load data from CSV and write it to Delta Lake in MinIO.
    """
    try:
        data_df = spark.read.format('csv') \
            .option('header', 'true') \
            .option('inferSchema', 'true') \
            .load(csv_path)
        print(f"Data loaded from {csv_path}.")

        data_df.write \
            .format("delta") \
            .partitionBy(partition_column) \
            .mode("overwrite") \
            .save(f"s3a://{bucket_name}/{output_path}")
        print(f"Data written to Delta Lake at s3a://{bucket_name}/{output_path}.")
    except Exception as e:
        sys.exit(f"Error loading/writing data: {e}")

def main():
    # Load environment variables
    env = load_environment_variables()

    # Initialize MinIO client
    client = initialize_minio_client(
        endpoint=env["MINIO_ENDPOINT"],
        access_key=env["MINIO_ACCESS_KEY"],
        secret_key=env["MINIO_SECRET_KEY"]
    )

    # Ensure the bucket exists
    ensure_bucket_exists(client, env["MINIO_BUCKET"])

    # Configure Spark session with Delta Lake
    delta_packages = ["org.apache.hadoop:hadoop-aws:3.3.4", "io.delta:delta-core_2.13:2.1.0"]
    spark = configure_spark_session(env["SPARK_APP_NAME"], delta_packages)

    # Set Spark Hadoop configurations
    hadoop_confs = {
        "fs.s3a.access.key": env["MINIO_ACCESS_KEY"],
        "fs.s3a.secret.key": env["MINIO_SECRET_KEY"],
        "fs.s3a.endpoint": env["MINIO_ENDPOINT"],
        "fs.s3a.path.style.access": "true",
        "fs.s3a.connection.ssl.enabled": "false",
        "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    }
    set_spark_hadoop_conf(spark, hadoop_confs)

    # Load data from CSV and write to Delta Lake
    load_and_write_data(
        spark=spark,
        csv_path=env["DATA_CSV_PATH"],
        bucket_name=env["MINIO_BUCKET"],
        output_path="data-delta",
        partition_column="school"
    )

    # Stop Spark session
    spark.stop()
    print("Spark session stopped.")

if __name__ == "__main__":
    main()
