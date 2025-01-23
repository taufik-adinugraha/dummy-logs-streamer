#!/usr/bin/env python3

import argparse
import os
import time
import random
import json
from faker import Faker
import boto3

fake = Faker()

STATUS_CODES = [200, 201, 400, 404, 500]
METHODS = ["GET", "POST", "PUT", "DELETE"]

def generate_json_logs(num_logs=50):
    logs = []
    for _ in range(num_logs):
        log_entry = {
            "timestamp": fake.iso8601(),
            "ip": fake.ipv4(),
            "method": random.choice(METHODS),
            "status": random.choice(STATUS_CODES),
            "url": fake.uri_path()
        }
        logs.append(log_entry)
    return logs

def main():
    parser = argparse.ArgumentParser(description="Generate JSON logs and upload to MinIO.")
    parser.add_argument("--minio-endpoint", required=True, help="MinIO endpoint, e.g. http://localhost:9000")
    parser.add_argument("--minio-access-key", required=True, help="MinIO access key")
    parser.add_argument("--minio-secret-key", required=True, help="MinIO secret key")
    parser.add_argument("--bucket", required=True, help="Name of the MinIO bucket to store logs")
    parser.add_argument("--prefix", default="json", help="Key prefix or 'folder' in the bucket")
    parser.add_argument("--num-logs", type=int, default=50, help="Number of log entries to generate")
    args = parser.parse_args()

    # 1. Generate JSON log entries
    logs = generate_json_logs(num_logs=args.num_logs)

    # 2. Write temporary JSON file (with JSON lines)
    ts_str = time.strftime("%Y%m%d_%H%M%S")
    filename = f"web_log_{ts_str}.json"
    with open(filename, "w", encoding="utf-8") as f:
        for log_entry in logs:
            f.write(json.dumps(log_entry) + "\n")

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
    print(f"[JSON LOGS] Successfully generated & uploaded {filename} to MinIO, then removed local file.")

if __name__ == "__main__":
    main()