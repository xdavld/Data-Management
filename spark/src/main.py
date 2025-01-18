import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import monotonically_increasing_id

def main():
    MINIO_URL = os.getenv("MINIO_URL")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

    spark = SparkSession.builder \
        .appName("Delta Lake to Minio") \
        .config("spark.jars", "/opt/spark/jars/delta-core_2.12-2.4.0.jar,/opt/spark/jars/hadoop-aws-3.4.0.jar,/opt/spark/jars/aws-java-sdk-bundle-1.12.277.jar") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_URL) \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()

    # Read the original CSV file
    df = spark.read.csv("/app/data/ds_salaries.csv", header=True, inferSchema=True)

    # Employees table with ID
    employees_df = df.select(
        df.employee_residence.alias("employee_residence"),
        df.experience_level.alias("experience_level")
    ).distinct()
    employees_df = employees_df.withColumn("employee_id", monotonically_increasing_id())

    # Jobs table with ID
    jobs_df = df.select(
        df.job_title.alias("job_title"),
        df.employment_type.alias("employment_type"),
        df.remote_ratio.alias("remote_ratio"),
        df.company_location.alias("company_location"),
        df.company_size.alias("company_size")
    ).distinct()
    jobs_df = jobs_df.withColumn("job_id", monotonically_increasing_id())

    # Salaries table with ID
    salaries_df = df.select(
        df.work_year.alias("work_year"),
        df.salary.alias("salary"),
        df.salary_currency.alias("salary_currency"),
        df.salary_in_usd.alias("salary_in_usd"),
        df.employee_residence.alias("employee_residence"),
        df.job_title.alias("job_title")
    )
    salaries_df = salaries_df.withColumn("salary_id", monotonically_increasing_id())

    # Write the tables to Delta
    employees_df.write.format("delta").option("mergeSchema", "true").mode("overwrite").save("s3a://lakehouse-storage/delta-tables/employees/")
    jobs_df.write.format("delta").option("mergeSchema", "true").mode("overwrite").save("s3a://lakehouse-storage/delta-tables/jobs/")
    salaries_df.write.format("delta").option("mergeSchema", "true").mode("overwrite").save("s3a://lakehouse-storage/delta-tables/salaries/")

    spark.stop()

if __name__ == "__main__":
    main()
