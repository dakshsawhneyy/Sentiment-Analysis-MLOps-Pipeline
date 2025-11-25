import os
import joblib
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from minio import Minio
from minio.credentials import StaticProvider

load_dotenv()

# ---------- MinIO Config ----------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USER = os.getenv("MINIO_ROOT_USER")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")

client = Minio(
    endpoint=MINIO_ENDPOINT,
    credentials=StaticProvider(MINIO_USER, MINIO_PASSWORD),
    secure=False
)

MODEL_BUCKET = "models"

# ---------- Load model ----------
def download_from_minio():
    os.makedirs("artifacts", exist_ok=True)

    client.fget_object(bucket_name=MODEL_BUCKET, object_name="production_model.joblib", file_path="artifacts/model.joblib")
    client.fget_object(bucket_name=MODEL_BUCKET, object_name="production_vectorizer.joblib", file_path="artifacts/vectorizer.joblib")

    model = joblib.load("artifacts/model.joblib")
    vectorizer = joblib.load("artifacts/vectorizer.joblib")
    return model, vectorizer


model, vectorizer = download_from_minio()

# ---------- FastAPI App ----------
app = FastAPI()

class Item(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(item: Item):
    X = vectorizer.transform([item.text])
    pred = model.predict(X)[0]
    return {"prediction": int(pred)}
