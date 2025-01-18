import os
import time
import boto3
import pandas as pd

# Environment Variables from Compose
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = "lakehouse-storage"

def main():
    print("[INFO] Starting data processing and MinIO upload")

    csv_path = "/app/data/ds_salaries.csv"
    df = pd.read_csv(csv_path)
    print(f"[INFO] Loaded CSV with {len(df)} rows")

    parquet_filename = "/app/data/ds_salaries.parquet"
    df.to_parquet(parquet_filename, engine="pyarrow")
    print("[INFO] Converted CSV -> Parquet")

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

    # Scraper loop that appends new data
    print("[INFO] Starting scraper simulation...")
    while True:
        time.sleep(60)

        print("[SCRAPER]")

if __name__ == "__main__":
    main()