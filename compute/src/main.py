import os
import duckdb
import ibis

# Environment variables for MinIO credentials and endpoint
MINIO_KEY_ID = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET = os.getenv("MINIO_SECRET_KEY", "J@ckson123")
MINIO_REGION = os.getenv("MINIO_REGION", "eu-central-1")
MINIO_ENDPOINT = os.getenv("MINIO_URL", "http://minio:9000")

# Configure DuckDB with HTTPFS and Delta support
duckdb.sql("INSTALL httpfs;")
duckdb.sql("LOAD httpfs;")
duckdb.sql("INSTALL delta;")
duckdb.sql("LOAD delta;")

# Set S3 credentials in DuckDB
duckdb.sql(f"SET s3_access_key_id='{MINIO_KEY_ID}';")
duckdb.sql(f"SET s3_secret_access_key='{MINIO_SECRET}';")
duckdb.sql(f"SET s3_region='{MINIO_REGION}';")
duckdb.sql(f"SET s3_endpoint='{MINIO_ENDPOINT.replace('http://', '').replace('https://', '')}';")
duckdb.sql("SET s3_url_style='path';")
duckdb.sql("SET s3_use_ssl=false;")

# Define the path to the DuckDB database file
DB_PATH = "/app/duckdb-file/persistent.duckdb"

# Ensure the parent directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect to a persistent DuckDB database
con = duckdb.connect(database=DB_PATH, read_only=False)
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL delta; LOAD delta;")

# Define S3 secrets for accessing the Delta tables
con.execute(f"""
CREATE SECRET secret1 (
    TYPE S3,
    KEY_ID '{MINIO_KEY_ID}',
    SECRET '{MINIO_SECRET}',
    REGION '{MINIO_REGION}',
    ENDPOINT '{MINIO_ENDPOINT.replace('http://', '').replace('https://', '')}',
    URL_STYLE 'path',
    USE_SSL {'true' if MINIO_ENDPOINT.startswith('https://') else 'false'}
);
""")

# Load the three Delta tables
con.execute("""
CREATE OR REPLACE TABLE employees AS
SELECT *
FROM delta_scan('s3://lakehouse-storage/delta-tables/employees/')
""")

con.execute("""
CREATE OR REPLACE TABLE jobs AS
SELECT *
FROM delta_scan('s3://lakehouse-storage/delta-tables/jobs/')
""")

con.execute("""
CREATE OR REPLACE TABLE salaries AS
SELECT *
FROM delta_scan('s3://lakehouse-storage/delta-tables/salaries/')
""")

# Connect Ibis to the DuckDB database
ibis.set_backend("duckdb")
ibis_con = ibis.duckdb.connect(DB_PATH)

# Define the Ibis tables
employees = ibis_con.table("employees")
jobs = ibis_con.table("jobs")
salaries = ibis_con.table("salaries")

# Function to save Ibis expressions to DuckDB
def save_to_duckdb(ibis_expr, connection, table_name):
    df = ibis_expr.execute()
    
    connection.register("temp_df", df)
    
    connection.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_df")
    
    connection.unregister("temp_df")

# Example Analysis 1: Average Salary by Job Title
joined_job = salaries.join(jobs, salaries.job_title == jobs.job_title)

avg_salary_job = joined_job.group_by('job_title').aggregate(
    avg_salary=joined_job.salary.mean()
).order_by(
    ibis.desc('avg_salary')
)

print("Average Salary by Job Title:")
print(avg_salary_job.execute())

# Save the first analysis as a new table
save_to_duckdb(avg_salary_job, con, "avg_salary_by_job_title")

# Example Analysis 2: Salary Distribution by Experience Level
joined_experience = salaries.join(
    employees,
    salaries.employee_residence == employees.employee_residence
)

salary_distribution = joined_experience.group_by('experience_level').aggregate(
    avg_salary=joined_experience.salary.mean(),
    count=joined_experience.salary.count()
).order_by(
    ibis.desc('avg_salary')
)

print("\nSalary Distribution by Experience Level:")
print(salary_distribution.execute())

# Save the second analysis as a new table
save_to_duckdb(salary_distribution, con, "salary_distribution_by_experience")

# Example Analysis 3: Salary Trends Over Years
salary_trends = salaries.group_by(
    'work_year'
).aggregate(
    avg_salary=salaries.salary.mean(),
    count=salaries.salary.count()
).order_by(
    'work_year'
)

print("\nSalary Trends Over Years:")
print(salary_trends.execute())

# Save the third analysis as a new table
save_to_duckdb(salary_trends, con, "salary_trends_over_years")

# Example Analysis 4: Average Salary by Company Size
joined_company_size = salaries.join(
    jobs,
    salaries.job_title == jobs.job_title
)

avg_salary_size = joined_company_size.group_by('company_size').aggregate(
    avg_salary=joined_company_size.salary.mean(),
    count=joined_company_size.salary.count()
).order_by(
    ibis.desc('avg_salary')
)

print("\nAverage Salary by Company Size:")
print(avg_salary_size.execute())

# Save the fourth analysis as a new table
save_to_duckdb(avg_salary_size, con, "avg_salary_by_company_size")

# Example Analysis 5: Impact of Remote Ratio on Salary
joined_remote = salaries.join(
    jobs,
    salaries.job_title == jobs.job_title
)

avg_salary_remote = joined_remote.group_by('remote_ratio').aggregate(
    avg_salary=joined_remote.salary.mean(),
    count=joined_remote.salary.count()
).order_by(
    ibis.desc('avg_salary')
)

print("\nAverage Salary by Remote Ratio:")
print(avg_salary_remote.execute())

# Save the fifth analysis as a new table
save_to_duckdb(avg_salary_remote, con, "avg_salary_by_remote_ratio")

# Confirm saved tables
tables = con.execute("SHOW TABLES").fetchall()
print("\nSaved Tables in DuckDB:")
for table in tables:
    print(table[0])

con.close()