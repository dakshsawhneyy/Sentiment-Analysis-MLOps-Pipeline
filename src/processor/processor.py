import json
import os
import csv
from datetime import datetime
from minio import Minio
from dotenv import load_dotenv
import pandas as pd
import re

# Load environment variables
load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USER = os.getenv("MINIO_ROOT_USER")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")

RAW_BUCKET = "raw"
PROCESSED_BUCKET = "processed"

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
)

def clean_text(text):
    if text is None:
        return ""

    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove special chars
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def process_file(object_name):
    """Download raw file → clean → export processed file → upload to MinIO"""

    # 1. Download file from MinIO
    raw_tmp = "/tmp/raw.jsonl"
    processed_tmp = "/tmp/processed.csv"

    client.fget_object(RAW_BUCKET, object_name, raw_tmp)

    records = []
    with open(raw_tmp, "r") as f:
        for line in f:
            data = json.loads(line)
            cleaned = {
                "text": clean_text(
                    f"{data.get('title', '')} {data.get('genre','')} {data.get('description','')}"
                ),
                "year": data.get("year", ""),
                "label": 1  # placeholder (no ML labels yet)
            }
            records.append(cleaned)

    # Convert → DataFrame
    df = pd.DataFrame(records)

    # Save processed CSV
    df.to_csv(processed_tmp, index=False)

    # Upload processed file
    processed_name = object_name.replace(".jsonl", "_processed.csv")
    client.fput_object(PROCESSED_BUCKET, processed_name, processed_tmp)

    print(f"[PROCESSOR] Processed {len(df)} records → {processed_name}")

    # Cleanup
    os.remove(raw_tmp)
    os.remove(processed_tmp)


def process_all_raw_files():
    """Process every raw file that exists in MinIO raw bucket."""
    objects = client.list_objects(RAW_BUCKET)

    for obj in objects:
        if obj.object_name.endswith(".jsonl"):
            print(f"[PROCESSOR] Processing file → {obj.object_name}")
            process_file(obj.object_name)


if __name__ == "__main__":
    process_all_raw_files()
