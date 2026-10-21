"""
Shared data preparation for the Zomato analytics project.
==========================================================

The raw Zomato CSV has two quirks that must be handled consistently:

1. Some ``Time_Orderd`` / ``Time_Order_picked`` values are Excel-style
   day fractions (``0.458333333`` == 11:00), not ``HH:MM`` strings.
2. A small number of restaurant/delivery coordinate pairs are impossible
   for a food delivery (up to ~19,700 km apart).  Those distances are
   masked rather than allowed to distort averages, correlations and models.

Both ``app.py`` and ``pipeline_scripts/train_api_model.py`` import this
module, so the API and the trained model always agree.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

EARTH_RADIUS_KM = 6371.0
MAX_REASONABLE_DISTANCE_KM = 100.0

COLUMN_MAP = {
    "Time_taken (min)": "Time_taken_min",
    "Time_taken(min)": "Time_taken_min",
    "Delivery_person_Ratings": "Rating",
    "Delivery_person_Age": "Age",
    "Road_traffic_density": "Traffic",
    "Weather_conditions": "Weather",
    "Type_of_vehicle": "Vehicle_type",
    "Type_of_order": "Order_type",
}

FEATURE_COLS = [
    "distance_km",
    "Weather",
    "Traffic",
    "City",
    "Vehicle_type",
    "Vehicle_condition",
    "multiple_deliveries",
    "Festival",
    "Age",
    "Rating",
    "hour",
]

CAT_COLS = ["Weather", "Traffic", "City", "Vehicle_type", "Festival"]

_NULL_STRINGS = {"nan", "none", "nat", "null", ""}


def _normalise_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and turn literal 'nan' strings into real NaN."""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        s = df[col].astype("string").str.strip()
        s = s.mask(s.str.lower().isin(_NULL_STRINGS))
        df[col] = s
    return df


def parse_time_minutes(series: pd.Series) -> pd.Series:
    """Convert ``HH:MM``, ``HH:MM:SS``, ``24:XX`` or Excel fractions to minutes.

    Returns a float Series; unparseable / missing values are NaN.
    """
    s = series.astype("string").str.strip()
    s = s.str.replace(r"^24:", "00:", regex=True)

    dt = pd.to_datetime(s, format="%H:%M", errors="coerce")
    dt_sec = pd.to_datetime(s, format="%H:%M:%S", errors="coerce")
    dt = dt.fillna(dt_sec)

    minutes = dt.dt.hour.astype("float64") * 60 + dt.dt.minute.astype("float64")

    # Excel stores 11:00 as 0.458333...; 1.0 means 24:00.
    numeric = pd.to_numeric(s, errors="coerce")
    fraction_mask = minutes.isna() & numeric.notna()
    if fraction_mask.any():
        minutes = minutes.copy()
        minutes.loc[fraction_mask] = (numeric.loc[fraction_mask] * 1440.0).round()

    return minutes


def parse_hour(series: pd.Series) -> pd.Series:
    """Return the hour-of-day (0-23) for mixed-format time strings."""
    minutes = parse_time_minutes(series)
    return ((minutes // 60) % 24).astype("Int64")


def parse_dates(series: pd.Series) -> pd.Series:
    """Parse ISO (cleaned CSV) or DD-MM-YYYY (raw CSV) dates correctly."""
    s = series.astype("string").str.strip()
    iso_mask = s.str.match(r"^\d{4}-\d{2}-\d{2}", na=False)

    parsed = pd.to_datetime(s.where(iso_mask), errors="coerce")
    if (~iso_mask).any():
        fallback = pd.to_datetime(s.where(~iso_mask), dayfirst=True, errors="coerce")
        parsed = parsed.fillna(fallback)
    return parsed


def haversine_km(lat1, lon1, lat2, lon2) -> pd.Series:
    """Great-circle distance in km (vectorised)."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    a = np.clip(a, 0.0, 1.0)
    return EARTH_RADIUS_KM * 2.0 * np.arcsin(np.sqrt(a))


def _validated_distance(df: pd.DataFrame) -> pd.Series:
    required = [
        "Restaurant_latitude",
        "Restaurant_longitude",
        "Delivery_location_latitude",
        "Delivery_location_longitude",
    ]
    if all(c in df.columns for c in required):
        dist = haversine_km(
            df["Restaurant_latitude"],
            df["Restaurant_longitude"],
            df["Delivery_location_latitude"],
            df["Delivery_location_longitude"],
        )
    elif "delivery_distance_km" in df.columns:
        dist = pd.to_numeric(df["delivery_distance_km"], errors="coerce")
    else:
        dist = pd.Series(np.nan, index=df.index)

    dist = pd.to_numeric(dist, errors="coerce")
    return dist.where(dist.between(0.0, MAX_REASONABLE_DISTANCE_KM))


def prepare_dataframe(df: pd.DataFrame, *, impute: bool = True) -> pd.DataFrame:
    """Load-ready cleaning used by the API and the model-training script."""
    df = df.copy()
    df = _normalise_strings(df)
    df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns}, inplace=True)

    # ---- Target ---------------------------------------------------------
    if "Time_taken_min" not in df.columns:
        for col in df.columns:
            if "time_taken" in col.lower() or "time taken" in col.lower():
                df.rename(columns={col: "Time_taken_min"}, inplace=True)
                break
    if "Time_taken_min" not in df.columns:
        raise ValueError("Could not find the delivery-time target column.")

    target = df["Time_taken_min"]
    if not pd.api.types.is_numeric_dtype(target):
        target = pd.to_numeric(
            target.astype("string").str.extract(r"(\d+(?:\.\d+)?)", expand=False),
            errors="coerce",
        )
    df["Time_taken_min"] = pd.to_numeric(target, errors="coerce")
    df = df.dropna(subset=["Time_taken_min"]).copy()
    df["Time_taken_min"] = df["Time_taken_min"].round().astype(int)

    # ---- Numeric columns ------------------------------------------------
    for col in ["Age", "Rating", "Vehicle_condition", "multiple_deliveries"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 53 raw rows record an impossible 6.0 rating. Cap them unconditionally so
    # every consumer (impute=True or False) sees a valid 1-5 rating scale.
    if "Rating" in df.columns:
        df["Rating"] = df["Rating"].clip(1.0, 5.0)

    if impute:
        if "Age" in df.columns:
            df["Age"] = df["Age"].fillna(df["Age"].median()).round().astype(int)
        if "Rating" in df.columns:
            df["Rating"] = df["Rating"].fillna(df["Rating"].median())
        for col in ["Weather", "Traffic", "City"]:
            if col in df.columns:
                mode = df[col].mode(dropna=True)
                df[col] = df[col].fillna(mode.iloc[0] if len(mode) else "Unknown")
        if "Festival" in df.columns:
            df["Festival"] = df["Festival"].fillna("No")
        if "multiple_deliveries" in df.columns:
            mode = df["multiple_deliveries"].mode(dropna=True)
            df["multiple_deliveries"] = df["multiple_deliveries"].fillna(
                mode.iloc[0] if len(mode) else 0
            )
        for col in ["Vehicle_condition", "multiple_deliveries"]:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)

    # ---- Times ----------------------------------------------------------
    if "Time_Orderd" in df.columns and "Time_Order_picked" in df.columns:
        df["Time_Orderd"] = df["Time_Orderd"].fillna(df["Time_Order_picked"])

    if "Time_Orderd" in df.columns:
        ordered = parse_time_minutes(df["Time_Orderd"])
        if "Time_Order_picked" in df.columns:
            picked = parse_time_minutes(df["Time_Order_picked"])
        else:
            picked = pd.Series(np.nan, index=df.index)

        prep = picked - ordered
        prep = prep.where(prep >= 0, prep + 1440)
        if impute:
            prep = prep.fillna(prep.median())
        df["prep_time_min"] = prep.round()

        hours = ((ordered // 60) % 24).astype("Int64")
        if impute:
            mode = hours.mode(dropna=True)
            hours = hours.fillna(int(mode.iloc[0]) if len(mode) else 12)
        df["hour"] = hours.astype("int64")
        df["hour_of_day"] = df["hour"]

    # ---- Distance -------------------------------------------------------
    df["distance_km"] = _validated_distance(df)
    if "delivery_distance_km" in df.columns:
        df["delivery_distance_km"] = df["distance_km"]

    return df


def training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Rows complete enough to train the serving model."""
    cols = FEATURE_COLS + ["Time_taken_min"]
    return df.dropna(subset=cols).copy()
