import os
import joblib
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from dotenv import load_dotenv

from minio import Minio
from minio.credentials import StaticProvider

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

load_dotenv()

# ---------- MinIO Config ----------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USER = os.getenv("MINIO_ROOT_USER")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")

client = Minio(
    endpoint=MINIO_ENDPOINT,
    secure=False,
    credentials=StaticProvider(MINIO_USER, MINIO_PASSWORD)
)

MODEL_BUCKET = "models"

# ---------- Dummy drift calculation ----------
def compute_drift(text: str):
    """
    Placeholder drift logic (for now).
    Later we will calculate embedding drift vs baseline mean vector.
    """
    return len(text) % 10 / 10.0


# ---------- Prometheus Metrics ----------
PREDICTION_COUNT = Counter("prediction_requests_total", "Total predictions made")
PREDICTION_LATENCY = Histogram("prediction_latency_seconds", "Latency for predictions")
DRIFT_SCORE = Gauge("embedding_drift_score", "Current drift score of model")
MODEL_VERSION = Gauge("model_version", "Version number of running model")


# ---------- Load Model from MinIO ----------
def download_from_minio():
    os.makedirs("artifacts", exist_ok=True)

    client.fget_object(bucket_name=MODEL_BUCKET, object_name="production_model.joblib", file_path="artifacts/model.joblib")
    client.fget_object(bucket_name=MODEL_BUCKET, object_name="production_vectorizer.joblib", file_path="artifacts/vectorizer.joblib")

    model = joblib.load("artifacts/model.joblib")
    vectorizer = joblib.load("artifacts/vectorizer.joblib")
    return model, vectorizer


model, vectorizer = download_from_minio()

# Update model version gauge
MODEL_VERSION.set(1)


# ---------- FastAPI App ----------
app = FastAPI()

class Item(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
@PREDICTION_LATENCY.time()
def predict(item: Item):
    text = item.text

    # Vectorize
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]

    PREDICTION_COUNT.inc()

    drift = compute_drift(text)
    DRIFT_SCORE.set(drift)

    return {
        "prediction": int(pred),
        "drift_score": drift
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
