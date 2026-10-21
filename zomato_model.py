"""Serving-model training/evaluation helpers for the Zomato API."""
from __future__ import annotations

import numpy as np
import pandas as pd

from zomato_prep import CAT_COLS, FEATURE_COLS, training_frame


def train_model_bundle(df: pd.DataFrame, *, test_size: float = 0.2, random_state: int = 42):
    """Train the Random Forest used by ``/api/predict`` on a holdout split.

    The returned bundle stores the encoders, feature order, and an honest
    80/20 test-set metric report alongside the fitted model.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder

    data = training_frame(df)
    if data.empty:
        raise ValueError("No complete rows available to train the delivery model.")

    X = data[FEATURE_COLS].copy()
    y = data["Time_taken_min"].to_numpy()

    encoders = {}
    for col in CAT_COLS:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "r2": round(float(r2_score(y_test, predictions)), 4),
        "mae": round(float(mean_absolute_error(y_test, predictions)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, predictions))), 2),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "test_size": test_size,
        "random_state": random_state,
    }

    importance = (
        pd.Series(model.feature_importances_, index=FEATURE_COLS)
        .sort_values(ascending=False)
        .round(4)
        .to_dict()
    )

    return {
        "model": model,
        "encoders": encoders,
        "feature_cols": list(FEATURE_COLS),
        "cat_cols": list(CAT_COLS),
        "metrics": metrics,
        "feature_importance": importance,
        "training_rows": int(len(data)),
    }
