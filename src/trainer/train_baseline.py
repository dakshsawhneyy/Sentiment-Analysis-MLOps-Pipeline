import os
import glob
import pandas as pd
import joblib
from minio import Minio
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import mlflow
import mlflow.sklearn

load_dotenv()

# ---------- MinIO Configuration ----------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USER = os.getenv("MINIO_ROOT_USER")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
)

PROCESSED_BUCKET = "processed"
MODEL_BUCKET = "models"

# ---------- MLflow ----------
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# ---------- Load processed data ----------
def load_processed_data(local_folder="data/processed"):
    os.makedirs(local_folder, exist_ok=True)

    # List all processed files in MinIO
    objects = client.list_objects(PROCESSED_BUCKET)

    downloaded_files = []
    
    for obj in objects:
        if obj.object_name.endswith(".csv"):
            local_path = os.path.join(local_folder, obj.object_name)
            client.fget_object(PROCESSED_BUCKET, obj.object_name, local_path)
            downloaded_files.append(local_path)

    if len(downloaded_files) == 0:
        raise Exception("No processed CSVs found in MinIO!")

    # Load all CSV files
    dfs = [pd.read_csv(f) for f in downloaded_files]
    df = pd.concat(dfs, ignore_index=True)

    print(f"[TRAIN] Loaded {df.shape[0]} rows from {len(downloaded_files)} processed files")
    return df


# ---------- Train baseline model ----------
def train_model(df):
    X = df["text"]
    y = df["label"]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2)
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)

    model = LogisticRegression(max_iter=2000)
    model.fit(X_train_vec, y_train)

    preds = model.predict(X_val_vec)

    acc = accuracy_score(y_val, preds)
    f1 = f1_score(y_val, preds, average="weighted")

    return model, vectorizer, acc, f1


# ---------- Upload model to MinIO ----------
def upload_model_to_minio(model_path, vectorizer_path):
    client.fput_object(MODEL_BUCKET, "model.joblib", model_path)
    client.fput_object(MODEL_BUCKET, "vectorizer.joblib", vectorizer_path)
    print("[TRAIN] Uploaded model + vectorizer → MinIO")


# ---------- Main ----------
if __name__ == "__main__":
    df = load_processed_data()

    with mlflow.start_run():

        model, vectorizer, acc, f1 = train_model(df)

        print(f"[TRAIN] Accuracy: {acc}")
        print(f"[TRAIN] F1 Score: {f1}")

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)

        # Save artifacts locally
        os.makedirs("artifacts", exist_ok=True)
        joblib.dump(model, "artifacts/model.joblib")
        joblib.dump(vectorizer, "artifacts/vectorizer.joblib")

        mlflow.log_artifact("artifacts/model.joblib")
        mlflow.log_artifact("artifacts/vectorizer.joblib")

        upload_model_to_minio(
            "artifacts/model.joblib",
            "artifacts/vectorizer.joblib"
        )

        print("[TRAIN] Training + Logging Completed")
