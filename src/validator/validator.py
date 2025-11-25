import os
import glob
import joblib
import pandas as pd
from minio import Minio
from sklearn.metrics import accuracy_score, f1_score
from dotenv import load_dotenv

load_dotenv()

# ----- MinIO Config -----
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
PROD_BUCKET = "production"

os.makedirs("artifacts", exist_ok=True)

# ----- Load Validation Dataset -----
def load_validation_data(local_folder="data/processed"):
    csv_files = glob.glob(f"{local_folder}/*.csv")
    if len(csv_files) == 0:
        raise Exception("No validation data found!")

    dfs = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(dfs, ignore_index=True)
    print(f"[VALIDATOR] Loaded {df.shape[0]} rows")
    return df


# ----- Download Model From MinIO -----
def download_model(model_name, local_path):
    try:
        client.fget_object(MODEL_BUCKET, model_name, local_path)
        return True
    except:
        return False


# ----- Evaluate Model -----
def evaluate(model, vectorizer, df):
    X = vectorizer.transform(df["text"])
    y = df["label"]

    preds = model.predict(X)

    acc = accuracy_score(y, preds)
    f1 = f1_score(y, preds, average="weighted")

    return acc, f1


if __name__ == "__main__":
    df = load_validation_data()

    # ----- Load NEW Model -----
    new_model_path = "artifacts/new_model.joblib"
    new_vec_path = "artifacts/new_vectorizer.joblib"

    download_model("model.joblib", new_model_path)
    download_model("vectorizer.joblib", new_vec_path)

    new_model = joblib.load(new_model_path)
    new_vec = joblib.load(new_vec_path)

    new_acc, new_f1 = evaluate(new_model, new_vec, df)
    print(f"[VALIDATOR] New model → acc={new_acc}, f1={new_f1}")

    # ----- Load Old (Production) Model -----
    old_model_path = "artifacts/old_model.joblib"
    old_vec_path = "artifacts/old_vectorizer.joblib"

    prod_exists = download_model("production_model.joblib", old_model_path)

    if prod_exists:
        download_model("production_vectorizer.joblib", old_vec_path)
        old_model = joblib.load(old_model_path)
        old_vec = joblib.load(old_vec_path)
        old_acc, old_f1 = evaluate(old_model, old_vec, df)
        print(f"[VALIDATOR] Old model → acc={old_acc}, f1={old_f1}")
    else:
        print("[VALIDATOR] No production model found → approving new model.")
        old_f1 = -1  # force new model to pass

    # ----- Decision -----
    if new_f1 >= old_f1:
        print("[VALIDATOR] New model is better → marking as production!")

        client.fput_object("models", "production_model.joblib", new_model_path)
        client.fput_object("models", "production_vectorizer.joblib", new_vec_path)

        print("[VALIDATOR] Uploaded new model as production version.")
    else:
        print("[VALIDATOR] New model is worse → rejecting it.")
