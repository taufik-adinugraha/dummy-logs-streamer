# Logs Generator for Data Lake

## Overview

This repository contains three Python scripts that generate synthetic log data (using Faker) and upload the files directly to a MinIO (S3-compatible) bucket:

1. `csv_log_generator.py` – Generates CSV-formatted logs (e.g., application logs)
2. `json_log_generator.py` – Generates JSON lines logs (e.g., web server logs)
3. `parquet_log_generator.py` – Generates Parquet-formatted logs (e.g., system/security logs)

Each script:
* Generates a batch of logs with random/fake data (timestamps, user info, etc.)
* Saves them temporarily to a local file
* Uploads the file to a specified MinIO bucket (using boto3 with an S3-compatible endpoint)
* Deletes the local file after upload (to keep the environment clean)

## Requirements

* Python 3.7+ (recommended)
* The Python packages (install via `pip install -r requirements.txt`)
* An accessible MinIO (or S3-compatible) endpoint
* We must have a bucket already created in MinIO where the logs will be uploaded
* Example MinIO credentials:
  * Endpoint: `http://localhost:9000`
  * Access Key: `ACCESS_KEY`
  * Secret Key: `SECRET_KEY`

## Usage

Each script accepts command-line arguments for MinIO credentials and can be run independently. Below is the generic usage pattern (replace `<script_name>.py` with the specific file).

```bash
python <script_name>.py \
    --minio-endpoint "http://MINIO_HOST:9000" \
    --minio-access-key "MINIO_ACCESS_KEY" \
    --minio-secret-key "MINIO_SECRET_KEY" \
    --bucket "logs" \
    [other optional arguments...]
```

### 1. CSV Log Generator

* File: `csv_log_generator.py`
* Arguments:
  * `--minio-endpoint` (required): MinIO endpoint (e.g. http://localhost:9000)
  * `--minio-access-key` (required): MinIO access key
  * `--minio-secret-key` (required): MinIO secret key
  * `--bucket` (required): Name of the target MinIO bucket
  * `--prefix` (optional, default="csv"): S3 key prefix (folder) to store the CSV file
  * `--num-rows` (optional, default=100): Number of CSV log rows to generate

```bash
python csv_log_generator.py \
    --minio-endpoint "http://localhost:9000" \
    --minio-access-key "myAccessKey" \
    --minio-secret-key "mySecretKey" \
    --bucket "logs" \
    --prefix "csv_logs" \
    --num-rows 500
```

### 2. JSON Log Generator

* File: `json_log_generator.py`
* Arguments:
  * `--minio-endpoint` (required)
  * `--minio-access-key` (required)
  * `--minio-secret-key` (required)
  * `--bucket` (required)
  * `--prefix` (optional, default="json")
  * `--num-logs` (optional, default=50)

```bash
python json_log_generator.py \
    --minio-endpoint "http://localhost:9000" \
    --minio-access-key "myAccessKey" \
    --minio-secret-key "mySecretKey" \
    --bucket "logs" \
    --prefix "json_logs" \
    --num-logs 200
```

### 3. Parquet Log Generator

* File: `parquet_log_generator.py`
* Arguments:
  * `--minio-endpoint` (required)
  * `--minio-access-key` (required)
  * `--minio-secret-key` (required)
  * `--bucket` (required)
  * `--prefix` (optional, default="parquet")
  * `--num-logs` (optional, default=200)

```bash
python parquet_log_generator.py \
    --minio-endpoint "http://localhost:9000" \
    --minio-access-key "myAccessKey" \
    --minio-secret-key "mySecretKey" \
    --bucket "logs" \
    --prefix "parquet_logs" \
    --num-logs 1000
```

## How It Works

1. **Generate Fake Data**: Uses Faker to produce realistic timestamps, IPs, user IDs, etc.
2. **Write to Local File**: A temporary file is written out (.csv, .json, or .parquet)
3. **Upload to MinIO**: The script uses boto3 with our provided endpoint and credentials to upload the file to the specified bucket and prefix
4. **Clean Up**: The local file is deleted after successful upload

## Creating Iceberg Tables on MinIO Logs

### CSV Logs

Assume our logs land in s3a://logs/csv_logs/ (MinIO endpoint).
Open Trino CLI or a SQL client connected to Trino and run:

```sql
CREATE TABLE nessie.logdb.csv_app_logs (
    event_time VARCHAR,
    log_level VARCHAR,
    user_id INT,
    action VARCHAR,
    description VARCHAR
)
WITH (
    format = 'CSV',
    external_location = 's3a://logs/csv_logs/'
);
```

**Notes:**
- nessie is the catalog name in our Trino config
- logdb is the database (namespace)
- Adjust columns to match our CSV schema
- format = 'CSV' so Iceberg knows how to read them
- external_location points to MinIO

### JSON Logs

If we generated JSON logs in s3a://logs/json_logs/, we can define a table similarly:

```sql
CREATE TABLE nessie.logdb.json_web_logs (
    timestamp VARCHAR,
    ip VARCHAR,
    method VARCHAR,
    status INT,
    url VARCHAR
)
WITH (
    format = 'JSON',
    external_location = 's3a://logs/json_logs/'
);
```

### Parquet Logs

Likewise:

```sql
CREATE TABLE nessie.logdb.parquet_sys_logs (
    timestamp TIMESTAMP,
    hostname VARCHAR,
    severity VARCHAR,
    message VARCHAR
)
WITH (
    format = 'PARQUET',
    external_location = 's3a://logs/parquet_logs/'
);
```

### Querying the Tables

Now we can run queries like:

```sql
SELECT log_level, COUNT(*) 
FROM nessie.logdb.csv_app_logs
GROUP BY log_level;
```

Or:

```sql
SELECT
    date_trunc('hour', timestamp) AS hr,
    COUNT(*) AS total
FROM nessie.logdb.parquet_sys_logs
GROUP BY date_trunc('hour', timestamp)
ORDER BY hr;
```
