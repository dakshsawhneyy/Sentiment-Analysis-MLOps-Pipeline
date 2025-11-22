import csv
import json
import time
from datetime import datetime
from minio import Minio
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USER = os.getenv("MINIO_ROOT_USER")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET = "raw"  # we upload to raw bucket

# MinIO client
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False  # http, not https
)

def clean_text(text):
    """Basic cleaning: remove commas, quotes etc."""
    if text is None:
        return ""
    text = text.replace(",", " ").replace("\"", "")
    return text.strip()

def ingest_csv(csv_path):
    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {
                "title": clean_text(row.get("Title")),
                "genre": clean_text(row.get("Genre")),
                "description": clean_text(row.get("Description")),
                "year": row.get("Year")
            }
            records.append(record)

    timestamp = int(time.time())
    file_name = f"{timestamp}.jsonl"

    # Write JSONL locally
    with open(file_name, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    # Upload to MinIO
    client.fput_object(
        BUCKET,
        file_name,
        file_name,
    )

    print(f"[INGEST] Uploaded {len(records)} records → {file_name}")

    # Cleanup local file
    os.remove(file_name)

if __name__ == "__main__":
    ingest_csv("/app/data/raw/IMDB-Movie-Data.csv")  # change path if needed