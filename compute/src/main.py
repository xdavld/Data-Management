import os
import time
import boto3
import pandas as pd
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

# Environment Variables from Compose
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
BUCKET_NAME = "lakehouse-storage"

def main():
    print("[INFO] Starting data processing and MinIO upload")

    csv_path = "/app/data/ds_salaries.csv"
    df = pd.read_csv(csv_path)
    print(f"[INFO] Loaded CSV with {len(df)} rows")

    # Convert CSV to Parquet
    parquet_filename = "/app/data/ds_salaries.parquet"
    df.to_parquet(parquet_filename, engine="pyarrow")
    print("[INFO] Converted CSV -> Parquet")

    # Initialize boto3 S3 client for Parquet upload
    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_URL,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )
    s3_parquet_key = "ds_salaries.parquet"
    print(f"[INFO] Uploading {parquet_filename} to s3://{BUCKET_NAME}/{s3_parquet_key}")
    s3_client.upload_file(parquet_filename, BUCKET_NAME, s3_parquet_key)
    print("[INFO] Parquet upload completed.")

    # Initialize Spark session with Delta Lake support
    builder = SparkSession.builder.appName("DeltaLakeUpload") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_URL) \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.2.0")  # Adjust version as needed

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    # Convert DataFrame to Spark DataFrame
    spark_df = spark.read.csv(csv_path, header=True, inferSchema=True)

    # Define Delta Lake path
    delta_path = "/app/data/ds_salaries_delta"

    # Write Delta Lake table
    spark_df.write.format("delta").mode("overwrite").save(delta_path)
    print("[INFO] Converted CSV -> Delta Lake")

    # Upload Delta Lake directory to MinIO
    import subprocess
    delta_s3_key = "ds_salaries_delta/"
    print(f"[INFO] Uploading Delta Lake files from {delta_path} to s3://{BUCKET_NAME}/{delta_s3_key}")

    # Use AWS CLI or `mc` to upload the directory
    # Ensure AWS CLI is installed in the compute container
    # Alternatively, use boto3 to upload files recursively

    # Example using boto3 to upload Delta Lake files
    for root, dirs, files in os.walk(delta_path):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = os.path.join(delta_s3_key, os.path.relpath(file_path, delta_path))
            s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
            print(f"[INFO] Uploaded {file_path} to s3://{BUCKET_NAME}/{s3_key}")

    print("[INFO] Delta Lake upload completed.")

    # Scraper loop that appends new data
    print("[INFO] Starting scraper simulation...")
    while True:
        time.sleep(60)
        print("[SCRAPER] Appended new data to Delta table.")

if __name__ == "__main__":
    main()
