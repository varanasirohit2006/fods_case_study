"""Train the Random Forest used by the Flask API.

Run from anywhere:

    python pipeline_scripts/train_api_model.py

The script reads ``cleaned_zomato_data.csv`` (falling back to the raw CSV),
uses the exact same preprocessing as ``app.py``, evaluates an 80/20 holdout,
and writes a compressed ``rf_delivery_model.joblib`` bundle containing the
model, encoders, feature list, and test metrics.
"""
from __future__ import annotations

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import joblib
import pandas as pd

from zomato_model import train_model_bundle
from zomato_prep import prepare_dataframe

DATA_PATH = os.path.join(ROOT, "cleaned_zomato_data.csv")
FALLBACK_PATH = os.path.join(ROOT, "Zomato Dataset.csv")
MODEL_PATH = os.path.join(ROOT, "rf_delivery_model.joblib")


def main() -> None:
    source = DATA_PATH if os.path.exists(DATA_PATH) else FALLBACK_PATH
    if not os.path.exists(source):
        raise FileNotFoundError("No cleaned or raw Zomato CSV found.")

    print(f"Loading: {source}")
    df = prepare_dataframe(pd.read_csv(source), impute=True)
    print(f"Rows available for training: {len(df):,}")

    started = time.time()
    bundle = train_model_bundle(df)
    print(f"Trained in {time.time() - started:.1f}s")

    metrics = bundle["metrics"]
    print(
        "Holdout results: "
        f"R2={metrics['r2']:.4f} | MAE={metrics['mae']:.2f} min | "
        f"RMSE={metrics['rmse']:.2f} min "
        f"(train={metrics['n_train']:,}, test={metrics['n_test']:,})"
    )
    print("Top features:")
    for name, value in list(bundle["feature_importance"].items())[:6]:
        print(f"  {name:<26} {value * 100:5.2f}%")

    joblib.dump(bundle, MODEL_PATH, compress=3)
    size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"Saved: {MODEL_PATH} ({size_mb:.1f} MiB, compressed)")


if __name__ == "__main__":
    main()
