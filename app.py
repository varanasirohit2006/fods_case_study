"""
Zomato Food Delivery -- Flask REST API Backend
=============================================
Serves the cleaned Zomato dataset through REST endpoints for the React
dashboard, Power BI / Tableau integration, and ad-hoc analytics queries.

Run:
    pip install flask flask-cors pandas numpy scikit-learn joblib
    python app.py          # starts on http://localhost:5000
"""

import math
import os
import warnings

import numpy as np
import pandas as pd
from flask import Flask, Response, jsonify, request

try:
    from flask_cors import CORS
except ImportError:  # graceful fallback
    CORS = None

from zomato_prep import CAT_COLS, FEATURE_COLS, parse_dates, prepare_dataframe

warnings.filterwarnings("ignore")

# 
# App initialisation
# 
app = Flask(__name__)
# Preserve explicit dict ordering (e.g. feature importance is pre-sorted by rank).
app.json.sort_keys = False
if CORS is not None:
    CORS(app)  # allow all origins for local development

# 
# Load & clean the dataset once at startup
# 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "cleaned_zomato_data.csv")
FALLBACK_PATH = os.path.join(BASE_DIR, "Zomato Dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "rf_delivery_model.joblib")

if os.path.exists(DATA_PATH):
    _raw_df = pd.read_csv(DATA_PATH)
elif os.path.exists(FALLBACK_PATH):
    _raw_df = pd.read_csv(FALLBACK_PATH)
else:
    raise FileNotFoundError(
        "Neither 'cleaned_zomato_data.csv' nor 'Zomato Dataset.csv' found in project root."
    )

# One shared cleaning path for times, categories, and GPS distances.
df = prepare_dataframe(_raw_df, impute=True)

print(f"  Dataset loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")


# 
# Helper: make every value JSON-serialisable (no NaN / numpy)
# 
def _sanitise(obj):
    """Recursively convert numpy types & NaN -> Python-native types."""
    if isinstance(obj, dict):
        return {k: _sanitise(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitise(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if math.isnan(obj) else round(float(obj), 2)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


def safe_json(payload, status=200):
    """Return a sanitised JSON response."""
    return jsonify(_sanitise(payload)), status


# 
# ROUTES
# 

#  GET / -- Welcome page listing all endpoints 
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html><head><title>Zomato API</title>
    <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f9f9f9}
      h1{color:#e23744} a{color:#e23744}
      li{margin:6px 0} code{background:#eee;padding:2px 6px;border-radius:3px}
    </style></head><body>
    <h1> Zomato Delivery Analytics API</h1>
    <p>Foundation of Data Science -- Case Study Backend</p>
    <h3>Available Endpoints</h3>
    <ul>
      <li><code>GET</code> <a href="/api/kpis">/api/kpis</a> -- Key Performance Indicators</li>
      <li><code>GET</code> <a href="/api/delivery-time/by-city">/api/delivery-time/by-city</a></li>
      <li><code>GET</code> <a href="/api/delivery-time/by-weather">/api/delivery-time/by-weather</a></li>
      <li><code>GET</code> <a href="/api/delivery-time/by-traffic">/api/delivery-time/by-traffic</a></li>
      <li><code>GET</code> <a href="/api/delivery-time/by-vehicle">/api/delivery-time/by-vehicle</a></li>
      <li><code>GET</code> <a href="/api/delivery-time/by-hour">/api/delivery-time/by-hour</a></li>
      <li><code>GET</code> <a href="/api/delivery-time/by-festival">/api/delivery-time/by-festival</a></li>
      <li><code>GET</code> <a href="/api/partner-analysis">/api/partner-analysis</a></li>
      <li><code>GET</code> <a href="/api/top-combinations">/api/top-combinations</a></li>
      <li><code>GET</code> <a href="/api/decisions">/api/decisions</a></li>
      <li><code>GET</code> <a href="/api/filtered-data">/api/filtered-data</a> -- ?city=&weather=&traffic=&</li>
      <li><code>GET</code> <a href="/api/predict">/api/predict</a> -- ?distance=5&weather=Sunny&</li>
    </ul></body></html>
    """
    return Response(html, mimetype="text/html")


#  GET /api/kpis 
@app.route("/api/kpis")
def kpis():
    try:
        date_col = "Order_Date" if "Order_Date" in df.columns else None
        date_range = "N/A"
        if date_col:
            dates = parse_dates(df[date_col]).dropna()
            if len(dates):
                date_range = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"

        distances = df["distance_km"].dropna() if "distance_km" in df.columns else pd.Series(dtype=float)

        payload = {
            "total_orders": int(len(df)),
            "total_delivery_partners": int(df["Delivery_person_ID"].nunique()) if "Delivery_person_ID" in df.columns else None,
            "avg_delivery_time": round(df["Time_taken_min"].mean(), 2),
            "median_delivery_time": round(df["Time_taken_min"].median(), 2),
            "avg_rating": round(df["Rating"].mean(), 2) if "Rating" in df.columns else None,
            "total_cities": int(df["City"].nunique()) if "City" in df.columns else None,
            "date_range": date_range,
            "avg_distance_km": round(float(distances.mean()), 2) if len(distances) else None,
            "median_distance_km": round(float(distances.median()), 2) if len(distances) else None,
            "p99_distance_km": round(float(distances.quantile(0.99)), 2) if len(distances) else None,
        }
        return safe_json(payload)
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


#  Delivery-time breakdown helpers 
def _time_by(group_col, label):
    """Generic groupby -> stats for a categorical column."""
    try:
        tmp = df.dropna(subset=[group_col])
        grp = (
            tmp.groupby(group_col)["Time_taken_min"]
            .agg(["mean", "median", "std", "count"])
            .reset_index()
        )
        grp.columns = [label, "mean_time", "median_time", "std_time", "order_count"]
        grp = grp.sort_values("mean_time", ascending=False)
        return safe_json(grp.to_dict(orient="records"))
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


@app.route("/api/delivery-time/by-city")
def dt_city():
    return _time_by("City", "city")


@app.route("/api/delivery-time/by-weather")
def dt_weather():
    return _time_by("Weather", "weather")


@app.route("/api/delivery-time/by-traffic")
def dt_traffic():
    return _time_by("Traffic", "traffic")


@app.route("/api/delivery-time/by-vehicle")
def dt_vehicle():
    return _time_by("Vehicle_type", "vehicle_type")


@app.route("/api/delivery-time/by-festival")
def dt_festival():
    return _time_by("Festival", "festival")


@app.route("/api/delivery-time/by-hour")
def dt_hour():
    try:
        tmp = df.dropna(subset=["hour"])
        grp = (
            tmp.groupby("hour")["Time_taken_min"]
            .agg(["mean", "count"])
            .reset_index()
        )
        grp.columns = ["hour", "mean_time", "order_count"]
        grp["mean_time"] = grp["mean_time"].round(2)
        grp = grp.sort_values("hour")
        return safe_json(grp.to_dict(orient="records"))
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


#  GET /api/partner-analysis 
@app.route("/api/partner-analysis")
def partner_analysis():
    try:
        payload = {
            "avg_age": round(df["Age"].mean(), 1) if "Age" in df.columns else None,
            "avg_rating": round(df["Rating"].mean(), 2) if "Rating" in df.columns else None,
            "total_partners": int(df["Delivery_person_ID"].nunique()) if "Delivery_person_ID" in df.columns else None,
            "vehicle_distribution": (
                df["Vehicle_type"].value_counts().to_dict() if "Vehicle_type" in df.columns else {}
            ),
            "avg_delivery_time_by_age_group": None,
        }
        # Age-group analysis (local copy: do not mutate the shared DataFrame)
        if "Age" in df.columns:
            bins = [15, 25, 30, 35, 40, 50]
            labels = ["15-25", "26-30", "31-35", "36-40", "41-50"]
            age_frame = df[["Age", "Time_taken_min"]].copy()
            age_frame["age_group"] = pd.cut(
                age_frame["Age"], bins=bins, labels=labels, right=True, include_lowest=True
            )
            age_stats = (
                age_frame.groupby("age_group", observed=True)["Time_taken_min"]
                .mean()
                .round(2)
                .to_dict()
            )
            payload["avg_delivery_time_by_age_group"] = {
                str(k): float(v) for k, v in age_stats.items()
            }

        # Batching analysis
        if "multiple_deliveries" in df.columns:
            batch_stats = (
                df.groupby("multiple_deliveries")["Time_taken_min"].mean().round(2).to_dict()
            )
            payload["avg_delivery_time_by_batching"] = {
                str(int(k)): float(v) for k, v in batch_stats.items()
            }

        payload["avg_delivery_time_by_batching"] = payload.get(
            "avg_delivery_time_by_batching", {}
        )
        return safe_json(payload)
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


#  GET /api/top-combinations 
@app.route("/api/top-combinations")
def top_combinations():
    try:
        grp = (
            df.dropna(subset=["City", "Weather", "Traffic"])
            .groupby(["City", "Weather", "Traffic"])["Time_taken_min"]
            .agg(["mean", "median", "count"])
            .reset_index()
        )
        grp.columns = ["city", "weather", "traffic", "mean_time", "median_time", "order_count"]
        grp["mean_time"] = grp["mean_time"].round(2)
        grp["median_time"] = grp["median_time"].round(2)
        grp = grp[grp["order_count"] >= 10]  # filter for statistical reliability

        top10 = grp.nlargest(10, "mean_time").to_dict(orient="records")
        bottom10 = grp.nsmallest(10, "mean_time").to_dict(orient="records")

        return safe_json({"slowest_10": top10, "fastest_10": bottom10})
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


#  GET /api/decisions 
@app.route("/api/decisions")
def decisions():
    try:
        payload = {
            "decisions": [
                {
                    "id": 1,
                    "title": "Dynamic Traffic & Weather ETA Buffering",
                    "evidence": "Jam traffic averages 31.18 min vs 21.46 min in Low traffic (+9.71 min; z = +96.98, p < 1e-15). Cloudy and Fog average 28.92 and 28.74 min vs 21.86 min in Sunny conditions (+7.06 min max).",
                    "impact": "Adds +10 min buffers in jams and +7 min in low-visibility weather, reducing SLA breaches without padding every order.",
                    "tag": "ETA Policy",
                    "image": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=800&q=80",
                },
                {
                    "id": 2,
                    "title": "Fleet Electrification & Scooter Prioritization",
                    "evidence": "Scooters average 24.48 min and electric scooters 24.47 min vs 27.61 min for motorcycles (3.13 min faster; permutation p < 0.0002).",
                    "impact": "Saves about 3.1 minutes per delivery while cutting fuel emissions on metro routes.",
                    "tag": "Fleet Strategy",
                    "image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=800&q=80",
                },
                {
                    "id": 3,
                    "title": "Holiday & Festival Surge Fleet Deployment (+30%)",
                    "evidence": "Festival deliveries average 45.52 min vs 25.91 min on normal days (+19.61 min; z = +139.68, p < 1e-15; 896 vs 44,688 orders).",
                    "impact": "Deploys 30% additional fleet and premium surge payouts to protect sub-35 min SLAs during festivals.",
                    "tag": "Surge Operations",
                    "image": "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80",
                },
                {
                    "id": 4,
                    "title": "Vehicle Condition Floor (Condition >= 1)",
                    "evidence": "Condition-0 vehicles average 30.07 min vs 24.35 min for condition 1 and 24.45 min for condition 2 (n = 15,005 vs ~15,000 each). Condition 3 is a small non-monotonic group (26.49 min, n = 520).",
                    "impact": "Rejects condition-0 vehicles at onboarding, cutting a 5.7 min penalty; flags condition-3 vehicles for inspection.",
                    "tag": "Fleet Maintenance",
                    "image": "https://images.unsplash.com/photo-1526367790999-0150786686a2?auto=format&fit=crop&w=1000&q=80",
                },
                {
                    "id": 5,
                    "title": "Strict Order Batching Caps (Max 2 Orders)",
                    "evidence": "Solo = 22.88 min; 1 stacked = 26.72 min; 2 = 40.45 min; 3 = 47.82 min. A second order adds +13.73 min and three orders vs solo +24.94 min (permutation p < 0.0002).",
                    "impact": "Caps simultaneous dispatches at two and eliminates 3-order windows that erase per-customer transit gains.",
                    "tag": "Dispatch Algorithm",
                    "image": "https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=800&q=80",
                },
                {
                    "id": 6,
                    "title": "High-Rated Partner Routing for Premium & Far Deliveries",
                    "evidence": "Partners rated 4.5+ average 24.42 min vs 37.37 min for the 2.0-3.0 band (12.95 min faster); the 31-35 age band averages 29.65 min.",
                    "impact": "Routes high-value family meals and long-distance orders to the highest-rated partners.",
                    "tag": "Rider Allocation",
                    "image": "https://images.unsplash.com/photo-1617347454431-f49d7ff5c3b1?auto=format&fit=crop&w=1200&q=80",
                },
                {
                    "id": 7,
                    "title": "Hub Pre-Positioning Ahead of Dinner Peak (7-9 PM)",
                    "evidence": "Volume rises from 2,065 orders at 10 AM to 4,865 at 9 PM; the 7-9 PM dinner window averages 31.05 min vs 19.52 min in the 8-10 AM morning window (+11.53 min).",
                    "impact": "Pre-positions riders near high-density cloud kitchens by 6:45 PM, cutting pickup latency during the dinner surge.",
                    "tag": "Demand Synchrony",
                    "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
                },
            ]
        }
        return safe_json(payload)
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


#  GET /api/filtered-data 
@app.route("/api/filtered-data")
def filtered_data():
    try:
        result = df.copy()
        filters = {
            "city": "City",
            "weather": "Weather",
            "traffic": "Traffic",
            "festival": "Festival",
            "vehicle": "Vehicle_type",
            "order_type": "Order_type",
        }
        for param, col in filters.items():
            val = request.args.get(param)
            if val and col in result.columns:
                result = result[result[col].astype(str).str.lower() == val.strip().lower()]

        min_time = request.args.get("min_time", type=float)
        max_time = request.args.get("max_time", type=float)
        if min_time is not None:
            result = result[result["Time_taken_min"] >= min_time]
        if max_time is not None:
            result = result[result["Time_taken_min"] <= max_time]

        # Free-text search is applied before the 1,000-row display cap, so the
        # returned total_matching reflects the full filtered dataset.
        search = (request.args.get("search") or "").strip().lower()
        if search:
            mask = pd.Series(False, index=result.index)
            for col in ["ID", "Delivery_person_ID", "City"]:
                if col in result.columns:
                    mask = mask | result[col].astype(str).str.lower().str.contains(
                        search, regex=False, na=False
                    )
            result = result[mask]

        # Limit to 1000 rows for performance
        total = len(result)
        result = result.head(1000)

        # Convert to records, replacing NaN
        records = result.where(result.notna(), None).to_dict(orient="records")

        return safe_json({
            "total_matching": total,
            "returned": len(records),
            "data": records,
        })
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


#  GET /api/model-info 
_MODEL_BUNDLE = None


def _get_model_bundle():
    """Load the serving model once per process instead of on every request."""
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is not None:
        return _MODEL_BUNDLE

    import joblib

    if os.path.exists(MODEL_PATH):
        _MODEL_BUNDLE = joblib.load(MODEL_PATH)
    else:
        from zomato_model import train_model_bundle

        _MODEL_BUNDLE = train_model_bundle(df)
        joblib.dump(_MODEL_BUNDLE, MODEL_PATH, compress=3)
    return _MODEL_BUNDLE


@app.route("/api/model-info")
def model_info():
    try:
        bundle = _get_model_bundle()
        return safe_json(
            {
                "metrics": bundle.get("metrics", {}),
                "features": bundle.get("feature_cols", FEATURE_COLS),
                "feature_importance": dict(
                    sorted(
                        bundle.get("feature_importance", {}).items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                ),
            }
        )
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


#  GET /api/predict 
@app.route("/api/predict")
def predict():
    try:
        # Cached, shared model bundle (loaded once per process)
        bundle = _get_model_bundle()
        model = bundle["model"]
        encoders = bundle["encoders"]
        feature_cols = bundle.get("feature_cols", FEATURE_COLS)
        cat_cols = bundle.get("cat_cols", CAT_COLS)

        # Parse query parameters
        params = {
            "distance_km": request.args.get("distance", type=float, default=5.0),
            "Weather": request.args.get("weather", default="Sunny"),
            "Traffic": request.args.get("traffic", default="Medium"),
            "City": request.args.get("city", default="Metropolitian"),
            "Vehicle_type": request.args.get("vehicle", default="motorcycle"),
            "Vehicle_condition": request.args.get("vehicle_condition", type=int, default=1),
            "multiple_deliveries": request.args.get("multiple_deliveries", type=int, default=0),
            "Festival": request.args.get("festival", default="No"),
            "Age": request.args.get("age", type=int, default=30),
            "Rating": request.args.get("rating", type=float, default=4.5),
            "hour": request.args.get("hour", type=int, default=14),
        }

        # Encode categorical features (reject unknown values explicitly)
        row = []
        for c in feature_cols:
            val = params[c]
            if c in cat_cols:
                le = encoders[c]
                if str(val) not in set(le.classes_):
                    return safe_json(
                        {
                            "error": f"Unknown value for '{c}': {val}",
                            "allowed": [str(x) for x in le.classes_],
                        },
                        400,
                    )
                val = int(le.transform([str(val)])[0])
            row.append(val)

        prediction = model.predict([row])[0]

        return safe_json({
            "predicted_delivery_time_min": round(float(prediction), 1),
            "input_parameters": params,
            "model_metrics": bundle.get("metrics", {}),
        })
    except Exception as e:
        return safe_json({"error": str(e)}, 500)


# 
# Run the server
# 
if __name__ == "__main__":
    host = os.environ.get("ZOMATO_API_HOST", "127.0.0.1")
    port = int(os.environ.get("ZOMATO_API_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"\n  Starting Zomato Analytics API on http://{host}:{port}\n")
    print("  Pre-loading Random Forest model bundle...")
    _get_model_bundle()
    print("  Model bundle ready — /api/predict is warm.\n")
    app.run(host=host, port=port, debug=debug)
