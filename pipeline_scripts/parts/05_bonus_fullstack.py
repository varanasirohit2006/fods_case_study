# =============================================================================
# LEGACY PIPELINE PART - NOT THE CANONICAL DELIVERABLE
# =============================================================================
# The canonical, fully executed analysis is Zomato_FoDS_Case_Study.ipynb.
# This part is retained for reference and writes only to legacy_outputs/.
# =============================================================================

import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LEGACY_OUTPUT_DIR = BASE_DIR / "legacy_outputs"
LEGACY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
# %% [markdown]
# # Bonus: Full-Stack Integration
#
# This notebook documents the **Flask REST API backend** that serves the
# cleaned Zomato delivery dataset and demonstrates how to connect it to
# enterprise BI tools -- **Power BI** and **Tableau**.
#
# ---
#
# ## Architecture Overview
#
# ```
# ┌───────────────────────────────────────────────────────────────────┐
# │                    ZOMATO ANALYTICS PLATFORM                     │
# │                                                                  │
# │  ┌──────────────┐     ┌──────────────────┐    ┌──────────────┐  │
# │  │  Raw CSV /   │────▶│  Flask REST API   │◀───│  Power BI /  │  │
# │  │  Cleaned CSV │     │  (app.py :5000)   │    │  Tableau     │  │
# │  └──────────────┘     └────────┬─────────┘    └──────────────┘  │
# │                                │                                 │
# │                     ┌──────────v─────────┐                      │
# │                     │   Endpoints:       │                      │
# │                     │   /api/kpis        │                      │
# │                     │   /api/delivery-*  │                      │
# │                     │   /api/predict     │                      │
# │                     │   /api/decisions   │                      │
# │                     │   /api/filtered-*  │                      │
# │                     └────────────────────┘                      │
# └───────────────────────────────────────────────────────────────────┘
# ```
#
# **Key components:**
# - **Data Layer** -- cleaned CSV loaded into a Pandas DataFrame at startup
# - **API Layer** -- Flask app with 13 RESTful endpoints (CORS-enabled)
# - **ML Layer** -- Random Forest model trained inline or loaded from cache
# - **BI Layer** -- Power BI / Tableau connect via Web connector or REST

# %% [markdown]
# ## 1. Starting the Flask Backend
#
# Open a terminal in the project directory and run:
#
# ```bash
# pip install flask flask-cors pandas numpy scikit-learn joblib
# python app.py
# ```
#
# The API starts on **http://127.0.0.1:5000**. Debug/reload mode is opt-in with
# `FLASK_DEBUG=1` (never enable it in production).

# %% [markdown]
# ## 2. API Endpoints Reference
#
# | Endpoint | Method | Description |
# |---|---|---|
# | `/` | GET | HTML index listing all endpoints |
# | `/api/kpis` | GET | Total orders, avg delivery time, avg rating, etc. |
# | `/api/delivery-time/by-city` | GET | Mean/median delivery time per city type |
# | `/api/delivery-time/by-weather` | GET | Delivery stats per weather condition |
# | `/api/delivery-time/by-traffic` | GET | Delivery stats per traffic density |
# | `/api/delivery-time/by-vehicle` | GET | Delivery stats per vehicle type |
# | `/api/delivery-time/by-hour` | GET | Hourly delivery time pattern |
# | `/api/delivery-time/by-festival` | GET | Festival vs non-festival comparison |
# | `/api/partner-analysis` | GET | Rider age, rating, vehicle distribution |
# | `/api/top-combinations` | GET | Top 10 slowest & fastest city+weather+traffic combos |
# | `/api/decisions` | GET | 7 evidence-based business decisions |
# | `/api/filtered-data` | GET | Filter rows by city, weather, traffic, etc. (max 1000) |
# | `/api/predict` | GET | ML prediction: estimated delivery time |

# %% [markdown]
# ## 3. Testing the API with Python `requests`
#
# The cell below sends requests to every endpoint and prints the response.
# **Make sure `app.py` is running** before executing this cell.

# %%
import requests
import json

BASE = "http://localhost:5000"

endpoints = [
    "/api/kpis",
    "/api/delivery-time/by-city",
    "/api/delivery-time/by-weather",
    "/api/delivery-time/by-traffic",
    "/api/delivery-time/by-vehicle",
    "/api/delivery-time/by-hour",
    "/api/delivery-time/by-festival",
    "/api/partner-analysis",
    "/api/top-combinations",
    "/api/decisions",
    "/api/filtered-data?city=Metropolitian&traffic=Jam",
    "/api/predict?distance=8&weather=Fog&traffic=Jam&city=Metropolitian&vehicle=motorcycle&age=28&rating=4.5&hour=19",
]

for ep in endpoints:
    try:
        r = requests.get(f"{BASE}{ep}", timeout=10)
        data = r.json()
        preview = json.dumps(data, indent=2)[:300]   # truncated preview
        print(f"✅  {ep}")
        print(f"    Status: {r.status_code}")
        print(f"    Preview: {preview}...")
        print()
    except requests.ConnectionError:
        print(f"❌  {ep} -- Connection refused. Is app.py running?")
    except Exception as e:
        print(f"⚠  {ep} -- {e}")

# %% [markdown]
# ## 4. Connecting Power BI to the API
#
# ### Step-by-step:
#
# 1. **Start the Flask server** -- `python app.py` (keep it running)
# 2. Open **Power BI Desktop** -> Get Data -> **Web**
# 3. Enter the URL: `http://localhost:5000/api/kpis`
# 4. Power BI will display the JSON. Click **"Into Table"** -> **Expand columns**
# 5. Repeat for other endpoints:
#    - `http://localhost:5000/api/delivery-time/by-city`
#    - `http://localhost:5000/api/delivery-time/by-weather`
#    - etc.
# 6. Each endpoint becomes a **separate query/table** in Power BI
# 7. Build dashboards using these tables:
#    - **KPI cards** from `/api/kpis`
#    - **Bar charts** from `/api/delivery-time/by-*` endpoints
#    - **Slicers** using the filtered-data endpoint
#
# ### Power Query M code (optional):
#
# ```m
# let
#     Source = Json.Document(Web.Contents("http://localhost:5000/api/delivery-time/by-city")),
#     Table  = Table.FromRecords(Source)
# in
#     Table
# ```
#
# ### Tip -- Auto-Refresh:
# Power BI can refresh from the API on schedule, giving you a **live dashboard**
# backed by the Flask backend.

# %% [markdown]
# ## 5. Connecting Tableau to the API
#
# ### Option A -- Web Data Connector (WDC)
#
# 1. Start the Flask server
# 2. In Tableau -> Data -> **Web Data Connector**
# 3. Enter: `http://localhost:5000/api/delivery-time/by-city`
# 4. Tableau fetches the JSON array and creates a data source
#
# ### Option B -- Export to SQLite (recommended for large data)
#
# The cell below exports the cleaned dataset to a SQLite database that
# Tableau can connect to natively.

# %%
import sqlite3
import pandas as pd
import os

csv_path = BASE_DIR / "Zomato Dataset.csv"
cleaned_path = LEGACY_OUTPUT_DIR / "cleaned_zomato_data.csv"

# Use whichever exists
data_path = cleaned_path if cleaned_path.exists() else csv_path
df = pd.read_csv(data_path)

db_path = LEGACY_OUTPUT_DIR / "zomato_analytics.db"
conn = sqlite3.connect(db_path)
df.to_sql("deliveries", conn, if_exists="replace", index=False)
conn.close()

print(f"✅  SQLite database created: {db_path}")
print(f"    Table 'deliveries' -- {len(df):,} rows")
print()
print("To connect Tableau:")
print("  1. Open Tableau -> Connect -> More -> SQLite")
print(f"  2. Browse to: {db_path}")
print("  3. Drag 'deliveries' table to the canvas")

# %% [markdown]
# ## 6. Summary
#
# | Integration | Method | Pros | Cons |
# |---|---|---|---|
# | **Power BI + Flask API** | Web connector (JSON) | Live data, easy refresh | Requires Flask server running |
# | **Tableau + Flask API** | Web Data Connector | Live data, real-time | Requires WDC setup |
# | **Tableau + SQLite** | Native connector | No server needed, fast | Static snapshot, manual export |
# | **Power BI + CSV** | File connector | Simplest setup | No API features, manual refresh |
#
# The Flask backend acts as a **single source of truth** for all BI tools,
# ensuring consistent KPI calculations and data transformations across
# every dashboard and report.
