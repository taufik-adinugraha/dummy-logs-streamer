#!/usr/bin/env python3

import argparse
import os
import time
import random
import pandas as pd
from faker import Faker
import boto3

fake = Faker()

def generate_parquet_logs(num_logs=200):
    data = {
        "timestamp": [],
        "hostname": [],
        "severity": [],
        "message": []
    }
    for _ in range(num_logs):
        data["timestamp"].append(fake.iso8601())
        data["hostname"].append(fake.hostname())
        data["severity"].append(random.choice(["low", "medium", "high"]))
        data["message"].append(fake.sentence(nb_words=8))
    df = pd.DataFrame(data)
    return df

def main():
    parser = argparse.ArgumentParser(description="Generate Parquet logs and upload to MinIO.")
    parser.add_argument("--minio-endpoint", required=True, help="MinIO endpoint, e.g. http://localhost:9000")
    parser.add_argument("--minio-access-key", required=True, help="MinIO access key")
    parser.add_argument("--minio-secret-key", required=True, help="MinIO secret key")
    parser.add_argument("--bucket", required=True, help="Name of the MinIO bucket to store logs")
    parser.add_argument("--prefix", default="parquet", help="Key prefix or 'folder' in the bucket")
    parser.add_argument("--num-logs", type=int, default=200, help="Number of log entries to generate")
    args = parser.parse_args()

    # 1. Generate a DataFrame of log data
    df = generate_parquet_logs(num_logs=args.num_logs)

    # 2. Write it to a temporary Parquet file
    ts_str = time.strftime("%Y%m%d_%H%M%S")
    filename = f"sys_log_{ts_str}.parquet"
    df.to_parquet(filename, index=False)

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
    print(f"[PARQUET LOGS] Successfully generated & uploaded {filename} to MinIO, then removed local file.")

if __name__ == "__main__":
    main()