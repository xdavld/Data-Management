from delta import *
from pyspark.sql import SparkSession
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables from Compose
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID",)
MINIO_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "lakehouse-storage"

# Initialize Spark session with Delta and S3A configurations
spark = (
    SparkSession.builder
    .appName("Minimal Delta Lake Example")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    .config("spark.hadoop.fs.s3a.endpoint", MINIO_URL)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .config("spark.hadoop.fs.s3a.connection.maximum", "100")
    .config("spark.hadoop.fs.s3a.connection.timeout", "5000")
    .config("spark.hadoop.fs.s3a.attempts.maximum", "3")
    .config("spark.hadoop.fs.s3a.retry.interval", "1000")
    .config("spark.hadoop.fs.s3a.fast.upload", "true")
    .config("spark.hadoop.fs.s3a.multipart.size", "104857600")  
    .master("spark://spark-master:7077")
    .getOrCreate()
)

try:
    # Define the S3A path for Delta table
    delta_path = f"s3a://{BUCKET_NAME}/delta-table"
    
    # Create a Delta table and write to MinIO
    data = spark.range(0, 5)
    logger.info(f"Writing Delta table to {delta_path}...")
    data.write.format("delta").mode("overwrite").save(delta_path)
    logger.info("Delta table written successfully.")
    
    # Read data from the Delta table
    logger.info(f"Reading Delta table from {delta_path}...")
    df = spark.read.format("delta").load(delta_path)
    df.show()
    logger.info("Delta table read successfully.")
    
except Exception as e:
    logger.error(f"An error occurred: {e}")
    
finally:
    spark.stop()
