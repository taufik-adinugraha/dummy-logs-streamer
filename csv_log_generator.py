#!/usr/bin/env python3

import argparse
import os
import time
import random
import csv
import uuid
from faker import Faker
import boto3

fake = Faker()

LOG_LEVELS = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]
COLUMNS = ["timestamp", "log_level", "user_id", "action", "description"]

def generate_csv_logs(num_rows=100):
    rows = []
    for _ in range(num_rows):
        timestamp = fake.iso8601()
        log_level = random.choice(LOG_LEVELS)
        user_id = fake.random_int(min=1000, max=9999)
        action = random.choice(["login", "logout", "update", "delete", "view"])
        description = f"User {user_id} performed {action}"
        rows.append([timestamp, log_level, user_id, action, description])
    return rows

def main():
    parser = argparse.ArgumentParser(description="Generate CSV logs and upload to MinIO.")
    parser.add_argument("--minio-endpoint", required=True, help="MinIO endpoint, e.g. http://localhost:9000")
    parser.add_argument("--minio-access-key", required=True, help="MinIO access key")
    parser.add_argument("--minio-secret-key", required=True, help="MinIO secret key")
    parser.add_argument("--bucket", required=True, help="Name of the MinIO bucket to store logs")
    parser.add_argument("--prefix", default="csv", help="Key prefix or 'folder' in the bucket")
    parser.add_argument("--num-rows", type=int, default=100, help="Number of log rows to generate")
    args = parser.parse_args()

    # 1. Generate CSV rows
    rows = generate_csv_logs(num_rows=args.num_rows)

    # 2. Create a temporary CSV file locally
    ts_str = time.strftime("%Y%m%d_%H%M%S")
    filename = f"app_log_{ts_str}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(COLUMNS)
        writer.writerows(rows)

    # 3. Upload to MinIO
    s3 = boto3.client(
        "s3",
        endpoint_url=args.minio_endpoint,
        aws_access_key_id=args.minio_access_key,
        aws_secret_access_key=args.minio_secret_key,
    )
    s3_key = f"{args.prefix}/{filename}"
    print(f"Uploading {filename} to s3://{args.bucket}/{s3_key}")
    s3.upload_file(filename, args.bucket, s3_key)

    # 4. Remove local file
    os.remove(filename)
    print(f"[CSV LOGS] Successfully generated & uploaded {filename} to MinIO, then removed local file.")

if __name__ == "__main__":
    main()