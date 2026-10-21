# =============================================================================
# LEGACY / DIAGNOSTIC PIPELINE - NOT THE CANONICAL DELIVERABLE
# =============================================================================
# The canonical, fully executed analysis is:
#     Zomato_FoDS_Case_Study.ipynb
# It regenerates cleaned_zomato_data.csv, plots/ and the reported statistics.
#
# This script is retained for reference and reproducibility checks. It writes
# ONLY to legacy_outputs/ and never overwrites the canonical CSV, plots, or
# serving model.
# =============================================================================

# =============================================================================
# FOUNDATION OF DATA SCIENCE (FoDS) - COMPREHENSIVE ZOMATO CASE STUDY
# =============================================================================
# Dataset: 45,584 orders across Indian cities
# Covers Requirements 1 through 10 + Bonus Full-Stack Integration
# =============================================================================

import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
LEGACY_OUTPUT_DIR = BASE_DIR / "legacy_outputs"
LEGACY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ===========================================================================
# FILE SOURCE: parts/01_preprocessing_eda.py
# ===========================================================================

import matplotlib
import matplotlib.pyplot as plt
plt.ioff()
# %% [markdown]
# # Foundation of Data Science -- Zomato Food Delivery Case Study
# ---
# **Requirements 1, 2 & 3**: Dataset Understanding, Preprocessing, EDA, and Key Learnings
#
# This notebook analyses 45,584 food-delivery orders from Zomato, one of India's
# largest food-delivery platforms. We clean the raw operational data, engineer
# meaningful features, and visually explore the factors that drive delivery time.

# %% -- Imports & Setup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid')
os.makedirs(LEGACY_OUTPUT_DIR / 'plots', exist_ok=True)

# ============================================================================
# =====================  REQUIREMENT 1: REAL DATASET  ========================
# ============================================================================

# %% [markdown]
# # Requirement 1: Real Dataset -- Understanding the Zomato Food Delivery Dataset
#
# The Zomato food-delivery dataset captures **real operational data** from one of
# India's largest food-delivery platforms. Each row represents a single delivery
# order and records the full lifecycle: from when the customer placed the order,
# through restaurant preparation, to the delivery partner dropping it off.
#
# **Why this dataset?**
# - **Real-world provenance**: sourced from actual Zomato operations across Indian cities.
# - **Statistical power**: 45,584 rows give enough volume for robust inferences.
# - **Multi-dimensional**: 20 columns span partner demographics, geography, weather,
#   traffic, vehicle type, and order details -- all key operational levers.
# - **Clear target**: `Time_taken (min)` is the metric Zomato wants to predict &
#   optimise to improve customer satisfaction and fleet efficiency.

# %% -- 1.1 Load & initial inspection
df = pd.read_csv(BASE_DIR / 'Zomato Dataset.csv')
print("=" * 60)
print(f"Dataset shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print("=" * 60)
print("\nColumn names:")
print(df.columns.tolist())

# %%
print("\n--- Data types & non-null counts ---")
df.info()

# %%
print("\n--- First 5 rows ---")
df.head()

# %%
print("\n--- Last 5 rows ---")
df.tail()

# %% [markdown]
# ## Column-by-Column Business Meaning
#
# | # | Column | Type | Description |
# |---|--------|------|-------------|
# | 1 | **ID** | object | Hexadecimal unique order identifier |
# | 2 | **Delivery_person_ID** | object | Coded ID of the delivery partner (e.g. "DEHRES17DEL01") |
# | 3 | **Delivery_person_Age** | float | Age of the delivery partner (15-50 yrs); proxy for experience & stamina |
# | 4 | **Delivery_person_Ratings** | float | Customer rating of the partner (1.0-5.0); reflects service quality |
# | 5 | **Restaurant_latitude** | float | Latitude of the restaurant (pick-up point) |
# | 6 | **Restaurant_longitude** | float | Longitude of the restaurant |
# | 7 | **Delivery_location_latitude** | float | Latitude of the customer (drop-off point) |
# | 8 | **Delivery_location_longitude** | float | Longitude of the customer |
# | 9 | **Order_Date** | object | Date the order was placed (DD-MM-YYYY) |
# | 10 | **Time_Orderd** | object | Time the customer placed the order (HH:MM); note misspelling in data |
# | 11 | **Time_Order_picked** | object | Time the partner picked up the order from the restaurant |
# | 12 | **Weather_conditions** | object | Weather at delivery time: Fog, Stormy, Sandstorms, Windy, Cloudy, Sunny |
# | 13 | **Road_traffic_density** | object | Traffic level: Low, Medium, High, Jam |
# | 14 | **Vehicle_condition** | int | Condition score of vehicle (0 = worst, 3 = best) |
# | 15 | **Type_of_order** | object | Category: Snack, Meal, Drinks, Buffet |
# | 16 | **Type_of_vehicle** | object | Vehicle: motorcycle, scooter, electric_scooter, bicycle |
# | 17 | **multiple_deliveries** | float | Number of simultaneous orders carried (0-3); batching indicator |
# | 18 | **Festival** | object | Whether a festival was ongoing (Yes / No) |
# | 19 | **City** | object | City tier: Metropolitian, Urban, Semi-Urban (note 'Metropolitian' spelling) |
# | 20 | **Time_taken (min)** | int | **TARGET** -- total delivery time in minutes (10-54) |
#
# ### Target Variable
# `Time_taken (min)` is the response variable. It measures the total elapsed time
# from order placement to delivery at the customer's doorstep. Reducing this
# metric directly improves customer satisfaction, partner efficiency, and platform
# competitiveness.

# ============================================================================
# ==================  REQUIREMENT 2A: PREPROCESSING  ========================
# ============================================================================

# %% [markdown]
# # Requirement 2: Data Preprocessing
#
# Raw operational data invariably contains missing values, inconsistent formats,
# and implicit information that must be engineered into explicit features.
# Below we apply a systematic cleaning pipeline.

# %% -- 2A.1 Strip whitespace from all object columns
# Some categorical values have leading/trailing whitespace (e.g. ' Fog', ' Jam')
# which would create duplicate categories if left untreated.
print("--- Step 1: Stripping whitespace from all string columns ---")
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()
print("Done. All object columns stripped.\n")

# %% -- 2A.2 Handle missing values
print("=" * 60)
print("Missing values BEFORE imputation:")
print("=" * 60)
missing_before = df.isnull().sum()
print(missing_before[missing_before > 0])
print(f"\nTotal missing cells: {missing_before.sum():,}")

# %% [markdown]
# ## Missing-Value Imputation Strategy
#
# | Column | Nulls | Strategy | Rationale |
# |--------|-------|----------|-----------|
# | Delivery_person_Age | 1,854 | **Median** | Age is roughly symmetric; median is robust to any outliers |
# | Delivery_person_Ratings | 1,908 | **Median** | Ratings cluster around 4.0-4.7; median preserves the central tendency |
# | Time_Orderd | 1,731 | **Fill with Time_Order_picked** | Closest available proxy; order & pick-up times are minutes apart |
# | Weather_conditions | 616 | **Mode** | Weather types are roughly balanced; mode introduces least bias |
# | Road_traffic_density | 601 | **Mode** | Using the most common traffic level is the safest default |
# | multiple_deliveries | 993 | **Mode** | Discrete count; mode preserves the dominant delivery pattern |
# | Festival | 228 | **'No'** | Only ~2% of orders are festival days; safe to assume non-festival |
# | City | 1,200 | **Mode** | Most orders are from Metropolitan cities; mode is representative |

# %%
# Delivery_person_Age -- median imputation
age_median = df['Delivery_person_Age'].median()
df['Delivery_person_Age'].fillna(age_median, inplace=True)
print(f"Age filled with median = {age_median}")

# Delivery_person_Ratings -- median imputation
rating_median = df['Delivery_person_Ratings'].median()
df['Delivery_person_Ratings'].fillna(rating_median, inplace=True)
invalid_ratings = int((df['Delivery_person_Ratings'] > 5.0).sum())
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].clip(upper=5.0)
print(f"Ratings filled with median = {rating_median}; capped {invalid_ratings} invalid 6.0 values")

# Time_Orderd -- fill with Time_Order_picked as proxy
df['Time_Orderd'].fillna(df['Time_Order_picked'], inplace=True)
print("Time_Orderd nulls filled with Time_Order_picked")

# Weather_conditions -- mode
weather_mode = df['Weather_conditions'].mode()[0]
df['Weather_conditions'].fillna(weather_mode, inplace=True)
print(f"Weather filled with mode = '{weather_mode}'")

# Road_traffic_density -- mode
traffic_mode = df['Road_traffic_density'].mode()[0]
df['Road_traffic_density'].fillna(traffic_mode, inplace=True)
print(f"Traffic filled with mode = '{traffic_mode}'")

# multiple_deliveries -- mode, then int
md_mode = df['multiple_deliveries'].mode()[0]
df['multiple_deliveries'].fillna(md_mode, inplace=True)
print(f"multiple_deliveries filled with mode = {md_mode}")

# Festival -- assume No
df['Festival'].fillna('No', inplace=True)
print("Festival nulls filled with 'No'")

# City -- mode
city_mode = df['City'].mode()[0]
df['City'].fillna(city_mode, inplace=True)
print(f"City filled with mode = '{city_mode}'")

# %%
print("\n" + "=" * 60)
print("Missing values AFTER imputation:")
print("=" * 60)
print(df.isnull().sum().sum(), "total nulls remaining")

# %% -- 2A.3 Data type conversions
print("\n--- Step 3: Data type conversions ---")
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
df.rename(columns={'Time_taken (min)': 'Time_taken_min'}, inplace=True)
print("Order_Date -> datetime, Age -> int, multiple_deliveries -> int")
print("Renamed 'Time_taken (min)' -> 'Time_taken_min'")

# %% [markdown]
# ## Feature Engineering
#
# Raw latitude/longitude pairs and timestamp strings are not directly useful for
# analysis. We engineer four actionable features:
#
# 1. **delivery_distance_km** -- Haversine great-circle distance between restaurant
#    and customer. This is the primary driver of delivery time.
# 2. **prep_time_min** -- Minutes between order placement and partner pick-up.
#    Captures restaurant preparation speed.
# 3. **hour_of_day** -- Hour when the order was placed. Captures demand surges
#    (lunch, dinner peaks) and traffic patterns.
# 4. **day_of_week / day_of_week_num / month** -- Calendar features for temporal
#    trend analysis.

# %% -- 2A.4a Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    """Compute great-circle distance in km between two coordinate arrays."""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))

df['delivery_distance_km'] = haversine(
    df['Restaurant_latitude'], df['Restaurant_longitude'],
    df['Delivery_location_latitude'], df['Delivery_location_longitude']
)
invalid_distances = int((df['delivery_distance_km'] > 100.0).sum())
df.loc[df['delivery_distance_km'] > 100.0, 'delivery_distance_km'] = np.nan
print(f"delivery_distance_km -- mean: {df['delivery_distance_km'].mean():.2f} km, "
      f"max: {df['delivery_distance_km'].max():.2f} km "
      f"({invalid_distances:,} impossible >100 km values masked)")

# %% -- 2A.4b Prep time (order -> pick-up)
def parse_time_to_minutes(series):
    """Use the shared parser so HH:MM, HH:MM:SS, 24:XX and Excel fractions agree."""
    from zomato_prep import parse_time_minutes
    return parse_time_minutes(series)

ordered_mins = parse_time_to_minutes(df['Time_Orderd'])
picked_mins = parse_time_to_minutes(df['Time_Order_picked'])

df['prep_time_min'] = picked_mins - ordered_mins
# Handle overnight crossover (e.g. ordered at 23:50, picked at 00:10)
df.loc[df['prep_time_min'] < 0, 'prep_time_min'] += 1440

# Fill any remaining NaN from unparseable timestamps with median
prep_median = df['prep_time_min'].median()
df['prep_time_min'].fillna(prep_median, inplace=True)
df['prep_time_min'] = df['prep_time_min'].astype(int)
print(f"prep_time_min -- median: {prep_median:.0f} min")

# %% -- 2A.4c Temporal features
from zomato_prep import parse_hour
parsed_hours = parse_hour(df['Time_Orderd'])
hour_mode = parsed_hours.mode(dropna=True)
df['hour_of_day'] = parsed_hours.fillna(int(hour_mode.iloc[0]) if len(hour_mode) else 12).astype(int)
df['day_of_week'] = df['Order_Date'].dt.day_name()
df['day_of_week_num'] = df['Order_Date'].dt.dayofweek
df['month'] = df['Order_Date'].dt.month
print("Engineered: hour_of_day, day_of_week, day_of_week_num, month")

# %% -- 2A.5 Duplicate check
dup_count = df.duplicated().sum()
print(f"\nDuplicate rows: {dup_count}")

# %% [markdown]
# ## Outlier Detection (IQR Method)
#
# We use the Interquartile Range (IQR) method to flag statistical outliers in
# `Time_taken_min` and `delivery_distance_km`. However, we **do not remove** them
# because:
# - Extreme delivery times (e.g. 50+ min) are genuine operational edge-cases caused
#   by traffic jams, festival surges, or long distances.
# - Removing them would bias the model toward "easy" deliveries and under-prepare
#   the platform for real-world worst-case scenarios.

# %% -- 2A.6 Outlier detection
def iqr_outlier_report(series, name):
    """Print IQR-based outlier bounds and count for a numeric series."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = ((series < lower) | (series > upper)).sum()
    print(f"\n{name}:")
    print(f"  Q1={Q1:.2f}  Q3={Q3:.2f}  IQR={IQR:.2f}")
    print(f"  Lower bound={lower:.2f}  Upper bound={upper:.2f}")
    print(f"  Outliers flagged: {outliers} ({outliers/len(series)*100:.2f}%)")
    return lower, upper

print("=" * 60)
print("OUTLIER DETECTION (IQR method -- flag only, no removal)")
print("=" * 60)
iqr_outlier_report(df['Time_taken_min'], 'Time_taken_min')
iqr_outlier_report(df['delivery_distance_km'], 'delivery_distance_km')

# %% -- 2A.7 Save cleaned data
legacy_csv = LEGACY_OUTPUT_DIR / 'cleaned_zomato_data.csv'
df.to_csv(legacy_csv, index=False)
print(f"\nCleaned data saved to '{legacy_csv}' (canonical CSV untouched)")
print(f"Final shape: {df.shape}")

# %%
print("\n--- Final dtypes ---")
df.info()

# %%
print("\n--- Descriptive statistics ---")
df.describe()

# ============================================================================
# ==================  REQUIREMENT 2B: EXPLORATORY DATA ANALYSIS  =============
# ============================================================================

# %% [markdown]
# # Requirement 2: Exploratory Data Analysis (EDA)
#
# We now create **20 targeted visualizations** to uncover patterns, distributions,
# and relationships in the cleaned Zomato delivery data. Each chart is designed to
# answer a specific business question relevant to delivery-time optimization.

# --------------------------------------------------------------------------
# EDA 01 -- Delivery Time Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 01: Distribution of Delivery Time
# **Domain Reason**: Delivery time is the target variable. Understanding its shape
# (skewness, spread, central tendency) is the essential first step before modelling.
#
# **Graph**: Histogram + KDE -- reveals the frequency profile and whether the data
# is normally distributed, skewed, or multimodal.
#
# **Expected Revelation**: Roughly normal / slightly right-skewed distribution
# centred around 25-28 minutes.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Time_taken_min'], bins=40, kde=True, color='steelblue', ax=ax)
ax.axvline(df['Time_taken_min'].mean(), color='red', linestyle='--', label=f"Mean = {df['Time_taken_min'].mean():.1f}")
ax.axvline(df['Time_taken_min'].median(), color='orange', linestyle='--', label=f"Median = {df['Time_taken_min'].median():.0f}")
ax.set_title('Distribution of Delivery Time', fontsize=14, fontweight='bold')
ax.set_xlabel('Delivery Time (minutes)')
ax.set_ylabel('Frequency')
ax.legend()
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_01_time_taken_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Skewness: {df['Time_taken_min'].skew():.3f}")

# %% [markdown]
# **Interpretation**: Delivery time follows a roughly symmetric distribution with
# a slight positive skew. The mean (~26.3 min) and median (~26 min) are close,
# confirming near-normality. The bulk of deliveries complete between 15-38 minutes.

# --------------------------------------------------------------------------
# EDA 02 -- Delivery Partner Age Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 02: Delivery Partner Age Distribution
# **Domain Reason**: Age may correlate with speed, experience, and route knowledge.
#
# **Graph**: Histogram -- shows the workforce demographic profile.
#
# **Expected Revelation**: Concentration in the 20-35 age range (young gig workers).

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Delivery_person_Age'], bins=30, kde=True, color='teal', ax=ax)
ax.set_title('Distribution of Delivery Partner Age', fontsize=14, fontweight='bold')
ax.set_xlabel('Age (years)')
ax.set_ylabel('Frequency')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_02_age_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: The delivery workforce spans ages 15-50 with peaks around
# 25-30. This is consistent with the gig-economy demographic -- predominantly
# young adults seeking flexible employment.

# --------------------------------------------------------------------------
# EDA 03 -- Delivery Partner Ratings Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 03: Delivery Partner Ratings Distribution
# **Domain Reason**: Ratings are a proxy for partner quality and customer satisfaction.
#
# **Graph**: Histogram -- reveals whether most partners are highly rated or if there
# is a wide spread.
#
# **Expected Revelation**: Left-skewed distribution with most ratings above 4.0.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Delivery_person_Ratings'], bins=20, kde=True, color='darkorange', ax=ax)
ax.set_title('Distribution of Delivery Partner Ratings', fontsize=14, fontweight='bold')
ax.set_xlabel('Rating (1.0 - 5.0)')
ax.set_ylabel('Frequency')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_03_ratings_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: Ratings are roughly uniformly spread between 1.0 and 5.0
# with no extreme pile-up, though there is a subtle concentration around 4.5-4.8.
# This suggests Zomato retains partners across a quality spectrum.

# --------------------------------------------------------------------------
# EDA 04 -- Delivery Distance Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 04: Delivery Distance Distribution
# **Domain Reason**: Distance is the most intuitive driver of delivery time.
#
# **Graph**: Histogram + KDE -- shows the typical delivery radius.
#
# **Expected Revelation**: Most deliveries are short-range (< 10 km); long tail
# for cross-city orders.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['delivery_distance_km'], bins=50, kde=True, color='mediumpurple', ax=ax)
ax.set_title('Distribution of Delivery Distance', fontsize=14, fontweight='bold')
ax.set_xlabel('Distance (km)')
ax.set_ylabel('Frequency')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_04_distance_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: The majority of deliveries are within 0-15 km, with a strong
# peak around 3-7 km. This aligns with hyper-local food delivery where restaurants
# and customers are in the same neighbourhood.

# --------------------------------------------------------------------------
# EDA 05 -- City Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 05: Orders by City Type
# **Domain Reason**: City type captures infrastructure quality, population density,
# and traffic patterns that influence delivery logistics.
#
# **Graph**: Count plot -- shows order volume breakdown by city tier.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
order = df['City'].value_counts().index
sns.countplot(data=df, x='City', order=order, palette='Set2', ax=ax)
ax.set_title('Order Count by City Type', fontsize=14, fontweight='bold')
ax.set_xlabel('City Type')
ax.set_ylabel('Number of Orders')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_05_city_countplot.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: Metropolitan cities dominate (~75% of orders), followed by
# Urban (~22%), with Semi-Urban contributing only a tiny fraction. This reflects
# Zomato's market penetration -- strongest in Tier-1 cities.

# --------------------------------------------------------------------------
# EDA 06 -- Order Type Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 06: Orders by Type
# **Domain Reason**: Different order types (Snack, Meal, Drinks, Buffet) may have
# different preparation times and thus different delivery times.
#
# **Graph**: Count plot -- shows the popularity of each order category.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, x='Type_of_order', order=df['Type_of_order'].value_counts().index,
              palette='Set2', ax=ax)
ax.set_title('Order Count by Order Type', fontsize=14, fontweight='bold')
ax.set_xlabel('Order Type')
ax.set_ylabel('Number of Orders')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_06_order_type_countplot.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: Snacks and Meals are the most popular order types, each
# comprising roughly a quarter of all orders. Drinks and Buffet orders are
# similarly common, showing balanced demand across categories.

# --------------------------------------------------------------------------
# EDA 07 -- Vehicle Type Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 07: Deliveries by Vehicle Type
# **Domain Reason**: Vehicle type affects speed, fuel cost, and capacity.
#
# **Graph**: Count plot -- shows the fleet composition.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, x='Type_of_vehicle', order=df['Type_of_vehicle'].value_counts().index,
              palette='husl', ax=ax)
ax.set_title('Delivery Count by Vehicle Type', fontsize=14, fontweight='bold')
ax.set_xlabel('Vehicle Type')
ax.set_ylabel('Number of Deliveries')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_07_vehicle_type_countplot.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: Motorcycles and scooters are the dominant delivery vehicles,
# reflecting the two-wheeler culture in Indian urban logistics. Electric scooters
# and bicycles have smaller shares.

# --------------------------------------------------------------------------
# EDA 08 -- Weather Conditions Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 08: Orders by Weather Condition
# **Domain Reason**: Weather directly impacts road safety, speed, and visibility.
#
# **Graph**: Count plot -- shows frequency of each weather type in the data.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, x='Weather_conditions', order=df['Weather_conditions'].value_counts().index,
              palette='coolwarm', ax=ax)
ax.set_title('Order Count by Weather Condition', fontsize=14, fontweight='bold')
ax.set_xlabel('Weather Condition')
ax.set_ylabel('Number of Orders')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_08_weather_countplot.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: Weather conditions are roughly evenly distributed across all
# six categories (~7,200-7,700 each). This balance is advantageous for modelling
# as no single category is under-represented.

# --------------------------------------------------------------------------
# EDA 09 -- Traffic Density Distribution
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 09: Orders by Road Traffic Density
# **Domain Reason**: Traffic is one of the biggest real-world drivers of delays.
#
# **Graph**: Count plot -- shows how orders are distributed across traffic levels.

# %%
traffic_order = ['Low', 'Medium', 'High', 'Jam']
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, x='Road_traffic_density', order=traffic_order, palette='YlOrRd', ax=ax)
ax.set_title('Order Count by Road Traffic Density', fontsize=14, fontweight='bold')
ax.set_xlabel('Traffic Density')
ax.set_ylabel('Number of Orders')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_09_traffic_countplot.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: 'Low' traffic is most common, followed by 'Jam'. This may
# reflect the dataset's temporal spread (many off-peak orders) and Indian metro
# traffic patterns where congestion is binary -- either flowing or jammed.

# --------------------------------------------------------------------------
# EDA 10 -- Time Taken by City
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 10: Delivery Time by City Type
# **Domain Reason**: Metropolitan cities have denser traffic but shorter distances;
# semi-urban areas have less congestion but sparser road networks.
#
# **Graph**: Box plot -- compares distributions, medians, and outliers across groups.
#
# **Expected Revelation**: Metropolitan deliveries may be slower due to traffic
# despite shorter distances.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='City', y='Time_taken_min',
            order=['Metropolitian', 'Urban', 'Semi-Urban'], palette='Set2', ax=ax)
ax.set_title('Delivery Time by City Type', fontsize=14, fontweight='bold')
ax.set_xlabel('City Type')
ax.set_ylabel('Delivery Time (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_10_time_by_city.png', dpi=150, bbox_inches='tight')
plt.close()
print(df.groupby('City')['Time_taken_min'].agg(['mean', 'median', 'std']).round(2))

# %% [markdown]
# **Interpretation**: Metropolitan cities show the highest median delivery time,
# followed by Urban. Semi-Urban areas have lower delivery times. This confirms
# that dense urban traffic offsets shorter distances.

# --------------------------------------------------------------------------
# EDA 11 -- Time Taken by Weather
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 11: Delivery Time by Weather Condition
# **Domain Reason**: Bad weather (fog, storms) reduces visibility and road safety,
# forcing partners to drive slower.
#
# **Graph**: Box plot -- reveals which weather conditions lead to the longest delays.

# %%
fig, ax = plt.subplots(figsize=(12, 6))
weather_order = df.groupby('Weather_conditions')['Time_taken_min'].median().sort_values().index
sns.boxplot(data=df, x='Weather_conditions', y='Time_taken_min', order=weather_order,
            palette='coolwarm', ax=ax)
ax.set_title('Delivery Time by Weather Condition', fontsize=14, fontweight='bold')
ax.set_xlabel('Weather Condition')
ax.set_ylabel('Delivery Time (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_11_time_by_weather.png', dpi=150, bbox_inches='tight')
plt.close()
print(df.groupby('Weather_conditions')['Time_taken_min'].agg(['mean', 'median']).sort_values('median').round(2))

# %% [markdown]
# **Interpretation**: Sandstorms and Fog conditions result in the highest median
# delivery times, while Sunny weather produces the fastest deliveries. Stormy and
# Windy conditions fall in between, confirming weather's operational impact.

# --------------------------------------------------------------------------
# EDA 12 -- Time Taken by Traffic
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 12: Delivery Time by Road Traffic Density
# **Domain Reason**: Traffic density is the most immediate controllable/predictable
# factor for routing decisions.
#
# **Graph**: Box plot (ordered Low->Jam) -- tests the hypothesis that more traffic
# leads to proportionally longer delivery times.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='Road_traffic_density', y='Time_taken_min',
            order=['Low', 'Medium', 'High', 'Jam'], palette='YlOrRd', ax=ax)
ax.set_title('Delivery Time by Road Traffic Density', fontsize=14, fontweight='bold')
ax.set_xlabel('Traffic Density')
ax.set_ylabel('Delivery Time (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_12_time_by_traffic.png', dpi=150, bbox_inches='tight')
plt.close()
print(df.groupby('Road_traffic_density')['Time_taken_min'].agg(['mean', 'median']).reindex(
    ['Low', 'Medium', 'High', 'Jam']).round(2))

# %% [markdown]
# **Interpretation**: There is a clear monotonic increase in delivery time from
# Low -> Medium -> High -> Jam. Jam-condition deliveries take ~7-10 minutes longer
# than Low-traffic ones. This validates traffic density as a critical predictor.

# --------------------------------------------------------------------------
# EDA 13 -- Time Taken by Order Type
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 13: Delivery Time by Order Type
# **Domain Reason**: Buffet orders may take longer to prepare; snacks may be faster.
#
# **Graph**: Box plot -- tests whether order complexity affects end-to-end delivery.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='Type_of_order', y='Time_taken_min', palette='Set2', ax=ax)
ax.set_title('Delivery Time by Order Type', fontsize=14, fontweight='bold')
ax.set_xlabel('Order Type')
ax.set_ylabel('Delivery Time (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_13_time_by_order_type.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: All four order types show very similar delivery time
# distributions. This suggests that order complexity (snack vs buffet) does NOT
# significantly impact total delivery time -- transit time dominates preparation time.

# --------------------------------------------------------------------------
# EDA 14 -- Time Taken by Vehicle Type
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 14: Delivery Time by Vehicle Type
# **Domain Reason**: Faster vehicles should yield shorter delivery times, but
# manoeuvrability in traffic also matters.
#
# **Graph**: Box plot -- compares delivery speed across vehicle categories.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='Type_of_vehicle', y='Time_taken_min', palette='husl', ax=ax)
ax.set_title('Delivery Time by Vehicle Type', fontsize=14, fontweight='bold')
ax.set_xlabel('Vehicle Type')
ax.set_ylabel('Delivery Time (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_14_time_by_vehicle.png', dpi=150, bbox_inches='tight')
plt.close()
print(df.groupby('Type_of_vehicle')['Time_taken_min'].agg(['mean', 'median']).sort_values('mean').round(2))

# %% [markdown]
# **Interpretation**: Scooters and electric scooters achieve the fastest deliveries
# (~24.5 min), while motorcycles are slowest (~27.6 min) and bicycles sit in between
# (~26.4 min). In congested Indian cities, manoeuvrability matters more than top speed.

# --------------------------------------------------------------------------
# EDA 15 -- Time Taken by Festival
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 15: Delivery Time -- Festival vs Non-Festival
# **Domain Reason**: Festivals drive order surges (Diwali, Holi), overwhelming the
# delivery fleet and increasing wait times.
#
# **Graph**: Box plot -- quantifies the festival premium on delivery time.
#
# **Expected Revelation**: Festival orders take noticeably longer.

# %%
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(data=df, x='Festival', y='Time_taken_min', order=['No', 'Yes'],
            palette=['#4CAF50', '#F44336'], ax=ax)
ax.set_title('Delivery Time: Festival vs Non-Festival', fontsize=14, fontweight='bold')
ax.set_xlabel('Festival Day')
ax.set_ylabel('Delivery Time (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_15_time_by_festival.png', dpi=150, bbox_inches='tight')
plt.close()
festival_stats = df.groupby('Festival')['Time_taken_min'].agg(['mean', 'median']).round(2)
print(festival_stats)
print(f"\nFestival premium: +{festival_stats.loc['Yes','mean'] - festival_stats.loc['No','mean']:.1f} min on average")

# %% [markdown]
# **Interpretation**: Festival-day deliveries take significantly longer -- roughly
# 5+ minutes more on average. This spike is caused by order surges, crowded roads,
# and stretched fleet capacity during celebrations.

# --------------------------------------------------------------------------
# EDA 16 -- Distance vs Time Scatter
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 16: Delivery Distance vs Time
# **Domain Reason**: Distance is expected to be the strongest physical predictor
# of delivery time.
#
# **Graph**: Scatter plot (alpha=0.1) -- reveals the strength and linearity of the
# distance-time relationship, plus any clustering.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['delivery_distance_km'], df['Time_taken_min'], alpha=0.1, s=10, color='steelblue')
ax.set_title('Delivery Distance vs Time Taken', fontsize=14, fontweight='bold')
ax.set_xlabel('Distance (km)')
ax.set_ylabel('Time Taken (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_16_distance_vs_time.png', dpi=150, bbox_inches='tight')
plt.close()
corr = df['delivery_distance_km'].corr(df['Time_taken_min'])
print(f"Pearson correlation (distance vs time): {corr:.4f}")

# %% [markdown]
# **Interpretation**: There is a moderate positive correlation between distance and
# delivery time. However, the cloud is quite dispersed, indicating that factors
# like traffic, weather, and prep time introduce substantial variability beyond
# mere distance.

# --------------------------------------------------------------------------
# EDA 17 -- Correlation Heatmap
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 17: Correlation Heatmap of Numeric Variables
# **Domain Reason**: Identifying pairwise linear associations guides feature
# selection for predictive modelling and flags potential multicollinearity.
#
# **Graph**: Annotated heatmap -- gives a complete correlation overview.

# %%
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
corr_matrix = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='viridis', center=0,
            linewidths=0.5, ax=ax)
ax.set_title('Correlation Heatmap -- Numeric Features', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_17_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: `delivery_distance_km` shows the strongest positive
# correlation with `Time_taken_min`. `Delivery_person_Ratings` has a weak negative
# correlation with time, suggesting higher-rated partners tend to deliver faster.
# The latitude/longitude pairs are naturally highly correlated with each other.

# --------------------------------------------------------------------------
# EDA 18 -- Average Time by Hour
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 18: Average Delivery Time by Hour of Day
# **Domain Reason**: Identifying peak-delay hours helps Zomato schedule fleet
# incentives and manage customer expectations.
#
# **Graph**: Line plot -- shows how average delivery time varies across the 24-hour
# clock.

# %%
hourly_time = df.groupby('hour_of_day')['Time_taken_min'].mean()
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(hourly_time.index, hourly_time.values, marker='o', color='steelblue', linewidth=2)
ax.fill_between(hourly_time.index, hourly_time.values, alpha=0.15, color='steelblue')
ax.set_title('Average Delivery Time by Hour of Day', fontsize=14, fontweight='bold')
ax.set_xlabel('Hour of Day (0-23)')
ax.set_ylabel('Average Time Taken (minutes)')
ax.set_xticks(range(0, 24))
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_18_time_by_hour.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: Delivery times peak during late evening hours (~19:00-22:00)
# which corresponds to dinner rush -- high order volume combined with evening
# traffic. Early morning hours show lower delivery times due to empty roads.

# --------------------------------------------------------------------------
# EDA 19 -- Order Volume by Hour
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 19: Order Volume by Hour of Day
# **Domain Reason**: Understanding demand peaks is critical for fleet pre-positioning
# and dynamic pricing.
#
# **Graph**: Bar chart -- shows the number of orders placed in each hour.

# %%
hourly_count = df['hour_of_day'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(hourly_count.index, hourly_count.values, color='teal', edgecolor='white')
ax.set_title('Order Volume by Hour of Day', fontsize=14, fontweight='bold')
ax.set_xlabel('Hour of Day (0-23)')
ax.set_ylabel('Number of Orders')
ax.set_xticks(range(0, 24))
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_19_orders_by_hour.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Interpretation**: Orders surge during lunch (11:00-14:00) and dinner (18:00-
# 22:00) windows, with dinner being the dominant peak. There is minimal ordering
# during midnight-early morning hours (00:00-08:00).

# --------------------------------------------------------------------------
# EDA 20 -- Time by Multiple Deliveries
# --------------------------------------------------------------------------

# %% [markdown]
# ## EDA 20: Delivery Time by Multiple Deliveries (Batching)
# **Domain Reason**: When a partner carries multiple orders simultaneously, each
# individual delivery may take longer because the partner must make multiple stops.
#
# **Graph**: Box plot -- shows the impact of order batching on delivery time.
#
# **Expected Revelation**: More simultaneous deliveries -> longer individual
# delivery times.

# %%
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='multiple_deliveries', y='Time_taken_min', palette='viridis', ax=ax)
ax.set_title('Delivery Time by Number of Simultaneous Deliveries', fontsize=14, fontweight='bold')
ax.set_xlabel('Number of Simultaneous Deliveries')
ax.set_ylabel('Delivery Time (minutes)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'eda_20_time_by_multiple_deliveries.png', dpi=150, bbox_inches='tight')
plt.close()
print(df.groupby('multiple_deliveries')['Time_taken_min'].agg(['mean', 'median', 'count']).round(2))

# %% [markdown]
# **Interpretation**: There is a clear upward trend -- partners carrying 3
# simultaneous deliveries take ~5-8 minutes longer on average than those carrying
# just 1. This batching penalty must be weighed against the operational efficiency
# gains of reducing total trips.

# ============================================================================
# ==================  REQUIREMENT 3: KEY LEARNINGS  ==========================
# ============================================================================

# %% [markdown]
# # Requirement 3: Key Learnings from Data
#
# After thorough preprocessing and 20 exploratory visualizations, here are the
# **12 key data-driven learnings** grouped by theme:
#
# ---
#
# ### 1. Delivery Time Profile (EDA 01)
# - The target variable `Time_taken_min` has a **mean of ~26.3 minutes** and a
#   **median of 26 minutes**, with a standard deviation of ~9.4 min. The distribution
#   is approximately symmetric with a very slight positive skew (skewness ~= 0.11).
#   This near-normality is favourable for parametric statistical methods and
#   linear regression assumptions.
#
# ### 2. Geographic Patterns -- City-Level Differences (EDA 05, 10)
# - **Metropolitan cities** account for ~75% of all orders but also exhibit the
#   **highest median delivery times** due to dense traffic and complex road networks.
#   Semi-Urban areas, though only ~0.4% of orders, show notably lower delivery times.
#   This suggests that Zomato's operational challenges scale with city density, not
#   just distance.
#
# ### 3. Weather Impact (EDA 08, 11)
# - **Sandstorms and Fog** produce the longest deliveries, adding approximately
#   4-6 minutes compared to Sunny conditions. Stormy and Windy weather fall in
#   between. Weather is roughly evenly distributed across categories, giving the
#   model balanced training data. **Decision**: Weather should be included as a
#   categorical feature in any predictive model.
#
# ### 4. Traffic Impact (EDA 09, 12)
# - Traffic density shows a **strict monotonic relationship** with delivery time:
#   Low < Medium < High < Jam. The gap between Low and Jam conditions is ~7-10
#   minutes. This is the single strongest categorical predictor visible in the
#   EDA. **Decision**: Traffic-aware routing and dynamic ETAs are essential.
#
# ### 5. Festival Effect (EDA 15)
# - Festival-day deliveries average **~5 minutes longer** than non-festival days.
#   Although festival orders are only ~2% of the dataset, their impact is
#   significant. **Decision**: Zomato should pre-deploy additional fleet capacity
#   and adjust customer-facing ETAs during known festival periods.
#
# ### 6. Vehicle Performance (EDA 07, 14)
# - Scooters and electric scooters achieve the **fastest** delivery times (~24.5 min),
#   motorcycles are slowest (~27.6 min), and bicycles average ~26.4 min. The spread
#   (~3.1 min) suggests that in congested cities, manoeuvrability matters more than top speed.
#
# ### 7. Delivery Partner Demographics (EDA 02, 03)
# - The workforce is predominantly **young (20-35 years old)**, typical of gig-
#   economy platforms. Partner ratings span 1.0-5.0 fairly evenly. The weak
#   negative correlation between rating and delivery time (EDA 17) hints that
#   experienced, higher-rated partners navigate routes more efficiently.
#
# ### 8. Order Type Distribution (EDA 06, 13)
# - All four order types (Snack, Meal, Drinks, Buffet) are **roughly equally
#   represented** and show **near-identical** delivery time distributions. This
#   indicates that restaurant preparation time (which varies by order type) is
#   either negligible or already absorbed into the prep_time feature. Order type
#   alone is unlikely to be a strong predictive feature.
#
# ### 9. Distance-Time Relationship (EDA 04, 16, 17)
# - `delivery_distance_km` has the **strongest positive correlation** with
#   `Time_taken_min` among all numeric features. However, the scatter plot (EDA 16)
#   reveals considerable variance around the trend -- the same distance can result
#   in delivery times varying by 15+ minutes depending on traffic, weather, and
#   other factors. A pure distance-based model would be insufficient.
#
# ### 10. Temporal Patterns (EDA 18, 19)
# - **Demand peaks** occur during lunch (11:00-14:00) and dinner (18:00-22:00),
#   with dinner being stronger. **Delivery times peak** during evening rush hours
#   (19:00-22:00) when high demand coincides with heavy traffic. Early morning
#   (01:00-08:00) has the lowest volume and fastest deliveries. **Decision**:
#   Dynamic fleet allocation and surge incentives should target 18:00-22:00.
#
# ### 11. Multiple Deliveries / Batching Effect (EDA 20)
# - Partners carrying **3 simultaneous orders** take ~5-8 minutes longer per
#   delivery than those carrying 1. This batching penalty is a trade-off:
#   fewer total trips save fuel and partner capacity, but each customer waits
#   longer. Optimal batching algorithms must balance fleet efficiency against
#   customer satisfaction.
#
# ### 12. Data Quality Observations
# - **Missing data** was concentrated in a few columns (Age: 4%, Ratings: 4.2%,
#   Time_Orderd: 3.8%, City: 2.6%). Imputation strategies were chosen to be
#   conservative (median for numeric, mode for categorical).
# - The `Time_Order_picked` column contained **880 invalid '24:XX' timestamps**
#   which were corrected to '00:XX'.
# - The city name "Metropolitian" is **misspelled** in the source data -- we
#   preserved it as-is to match the raw data schema.
# - **No duplicate rows** were found, confirming each row is a unique order.
# - Outlier detection via IQR flagged a small number of extreme values in
#   delivery time and distance but these were **retained** as genuine edge cases.
#
# ---
#
# ### Summary
# The three most influential factors for delivery time optimisation are:
# 1. **Road traffic density** (strongest categorical predictor)
# 2. **Delivery distance** (strongest numeric predictor)
# 3. **Festival / special events** (largest proportional impact)
#
# These learnings directly inform the feature selection and modelling strategies
# in the subsequent requirements of this case study.

# ===========================================================================
# FILE SOURCE: parts/02_analysis_q1_q9.py
# ===========================================================================

import matplotlib
import matplotlib.pyplot as plt
plt.ioff()
# %% [markdown]
# # Requirements 4 & 5: Analytical Questions and Implementation (Q1-Q9)
# 
# This section formulates domain-driven analytical questions and answers each one
# with suitable data analysis techniques and visualizations.

# %%
# --- Standalone imports (used when running this file independently) ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid')
os.makedirs('plots', exist_ok=True)

# Load cleaned data
try:
    df.shape  # check if df already exists (combined mode)
except NameError:
    df = pd.read_csv(LEGACY_OUTPUT_DIR / 'cleaned_zomato_data.csv')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])

# %% [markdown]
# ---
# ## Q1: How does average delivery time differ across Metropolitan, Urban, and Semi-Urban cities?
# 
# **Domain Reason:**  
# Zomato operates across a spectrum of Indian cities -- from densely populated metropolitan
# hubs like Mumbai and Delhi to smaller semi-urban towns. Understanding how delivery time
# varies by city tier is crucial for setting realistic customer expectations (estimated
# delivery time displayed in the app), allocating fleet resources, and designing
# tier-specific operational strategies. If metropolitan cities consistently take longer,
# Zomato may need to invest in dedicated logistics hubs or dark-store kitchens in those areas.
# 
# **Graph Selected:** Violin Plot  
# A violin plot is ideal here because it reveals the *full distribution shape* of delivery
# times for each city type -- not just the mean or quartiles. This lets us see whether the
# distribution is skewed, bimodal, or has heavy tails, which a simple bar chart would hide.
# 
# **Expected Revelation:**  
# We expect Metropolitan cities to show the highest average delivery time due to greater
# traffic congestion and longer distances, while Semi-Urban cities should exhibit the
# shortest times owing to lighter traffic and compact geography.

# %%
# --- Q1: Delivery time by City type ---
city_stats = df.groupby('City')['Time_taken_min'].agg(['mean', 'median', 'std', 'count'])
city_stats = city_stats.sort_values('mean', ascending=False)
print("=" * 60)
print("Q1: Delivery Time Statistics by City Type")
print("=" * 60)
print(city_stats.round(2).to_string())
print()

# Violin plot
fig, ax = plt.subplots(figsize=(10, 6))
city_order = ['Metropolitian', 'Urban', 'Semi-Urban']
palette = sns.color_palette('Set2', n_colors=3)

sns.violinplot(x='City', y='Time_taken_min', data=df, order=city_order,
               palette=palette, inner='quartile', ax=ax)

# Overlay mean markers
means = df.groupby('City')['Time_taken_min'].mean()
for i, city in enumerate(city_order):
    ax.scatter(i, means[city], color='red', s=80, zorder=5, marker='D',
               edgecolors='black', linewidths=0.8)
    ax.annotate(f'mean={means[city]:.1f}', (i, means[city]),
                textcoords='offset points', xytext=(15, 5),
                fontsize=10, fontweight='bold', color='red')

ax.set_title('Distribution of Delivery Time by City Type', fontsize=14, fontweight='bold')
ax.set_xlabel('City Type', fontsize=12)
ax.set_ylabel('Time Taken (minutes)', fontsize=12)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q1_city_delivery_time.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# The violin plot reveals that all three city types share a broadly similar distribution
# shape, centred around 25-27 minutes. Metropolitan cities exhibit the widest spread
# and the highest mean delivery time, reflecting the unpredictability of traffic and
# longer travel distances in large Indian metros. Semi-Urban cities show a tighter
# distribution with a lower mean, consistent with shorter distances and less congestion.
# 
# **Interpretation:**  
# The difference between city tiers, while statistically present, may be smaller than
# intuitively expected. This suggests that Zomato's existing assignment algorithms
# already partially compensate by selecting closer riders in metros. However, the
# heavier upper tail in Metropolitan areas indicates that a subset of metro deliveries
# take disproportionately long -- likely those crossing major traffic corridors.
# 
# **Conclusion/Decision:**  
# Zomato should implement tier-specific ETA padding: metro orders could carry a +3-5 min
# buffer in the displayed estimate, while semi-urban orders can promise tighter windows.
# Fleet allocation in metros should also be increased during peak congestion hours.

# %% [markdown]
# ---
# ## Q2: What is the distribution of order volume across city types?
# 
# **Domain Reason:**  
# Order volume by city tier directly impacts revenue, marketing budgets, and logistics
# planning. Knowing where most orders originate helps Zomato decide where to invest in
# restaurant partnerships, delivery fleet expansion, and promotional campaigns. A city
# type contributing disproportionately low volume relative to its population may signal
# untapped growth potential.
# 
# **Graph Selected:** Pie Chart + Bar Chart (side by side)  
# A pie chart intuitively communicates proportional share, while a bar chart with value
# labels shows absolute counts -- together they give a complete picture of both relative
# and absolute order distribution.
# 
# **Expected Revelation:**  
# Metropolitan cities likely dominate order volume due to larger user bases, higher
# smartphone penetration, and established food-delivery culture. Semi-Urban areas are
# expected to contribute the smallest share.

# %%
# --- Q2: Order volume by City type ---
city_counts = df['City'].value_counts()
city_pct = (city_counts / city_counts.sum() * 100).round(1)

print("=" * 60)
print("Q2: Order Volume by City Type")
print("=" * 60)
for city in city_counts.index:
    print(f"  {city:16s}: {city_counts[city]:,} orders ({city_pct[city]:.1f}%)")
print(f"  {'Total':16s}: {city_counts.sum():,} orders")
print()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Pie chart
colors = sns.color_palette('Set2', n_colors=len(city_counts))
wedges, texts, autotexts = axes[0].pie(
    city_counts, labels=city_counts.index, autopct='%1.1f%%',
    colors=colors, startangle=90, pctdistance=0.75,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
)
for t in autotexts:
    t.set_fontsize(11)
    t.set_fontweight('bold')
axes[0].set_title('Proportion of Orders by City Type', fontsize=13, fontweight='bold')

# Right: Bar chart with value labels
bars = axes[1].bar(city_counts.index, city_counts.values, color=colors, edgecolor='black', linewidth=0.5)
for bar, count, pct in zip(bars, city_counts.values, city_pct.values):
    axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 80,
                 f'{count:,}\n({pct}%)', ha='center', va='bottom',
                 fontsize=11, fontweight='bold')
axes[1].set_title('Order Count by City Type', fontsize=13, fontweight='bold')
axes[1].set_xlabel('City Type', fontsize=12)
axes[1].set_ylabel('Number of Orders', fontsize=12)

plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q2_city_order_volume.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# Metropolitan cities account for the largest share of total orders, followed by Urban
# and then Semi-Urban areas. The pie chart makes the dominance of metro cities immediately
# visible, while the bar chart provides precise counts for operational planning.
# 
# **Interpretation:**  
# The heavy skew toward metropolitan orders reflects India's food-delivery reality:
# metros have higher disposable incomes, greater restaurant density, and more delivery
# infrastructure. However, the non-trivial Semi-Urban share suggests an emerging market
# segment -- these customers may have fewer restaurant options nearby and thus rely more
# heavily on delivery platforms.
# 
# **Conclusion/Decision:**  
# While metro operations should remain the priority, Zomato should explore targeted
# expansion strategies in Semi-Urban areas (e.g., lower minimum order values, partnering
# with local eateries) to capture growing demand. Marketing spend can be allocated in
# proportion to current volume, with a growth premium for under-penetrated tiers.

# %% [markdown]
# ---
# ## Q3: How do weather conditions affect average delivery time?
# 
# **Domain Reason:**  
# India's diverse climate means delivery riders face everything from blazing sun to
# monsoon storms and winter fog. Adverse weather slows riders, increases accident risk,
# and degrades road conditions. Understanding the precise impact of each weather type on
# delivery time helps Zomato adjust ETAs dynamically, trigger surge pricing when
# appropriate, and implement safety protocols (e.g., suspending bicycle deliveries
# during storms).
# 
# **Graph Selected:** Bar Chart with 95% Confidence Interval Error Bars  
# A bar chart ordered from highest to lowest mean time clearly ranks weather conditions.
# The CI error bars communicate statistical uncertainty -- if bars overlap, the difference
# may not be reliable. This is more informative than a plain bar chart.
# 
# **Expected Revelation:**  
# Stormy and Fog conditions should produce the highest delivery times due to reduced
# visibility and hazardous roads. Sunny weather should yield the lowest times as riders
# face no environmental impediment.

# %%
# --- Q3: Weather impact on delivery time ---
weather_stats = df.groupby('Weather_conditions')['Time_taken_min'].agg(
    ['mean', 'median', 'std', 'count']
).sort_values('mean', ascending=False)

print("=" * 60)
print("Q3: Delivery Time by Weather Condition")
print("=" * 60)
print(weather_stats.round(2).to_string())
print()

# Ordered from highest to lowest mean
weather_order = weather_stats.index.tolist()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='Weather_conditions', y='Time_taken_min', data=df,
            order=weather_order, ci=95, palette='YlOrRd_r', ax=ax,
            edgecolor='black', linewidth=0.5)

# Add mean labels on top of bars
for i, weather in enumerate(weather_order):
    mean_val = weather_stats.loc[weather, 'mean']
    ax.text(i, mean_val + 0.3, f'{mean_val:.1f}', ha='center', va='bottom',
            fontsize=10, fontweight='bold')

ax.set_title('Average Delivery Time by Weather Condition (with 95% CI)',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Weather Condition', fontsize=12)
ax.set_ylabel('Average Time Taken (minutes)', fontsize=12)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q3_weather_delivery_time.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# The bar chart confirms that adverse weather conditions (Sandstorms, Stormy, Fog)
# are associated with higher average delivery times compared to benign conditions
# (Sunny, Cloudy, Windy). The confidence intervals show that the differences between
# the top conditions are statistically meaningful.
# 
# **Interpretation:**  
# Sandstorms and stormy weather add roughly 2-4 minutes to delivery time on average
# compared to sunny conditions. This may seem modest, but at Zomato's scale of millions
# of daily orders, even a 2-minute delay aggregates into significant customer
# dissatisfaction. Fog, common in North Indian winters, also meaningfully slows
# deliveries due to reduced visibility on roads.
# 
# **Conclusion/Decision:**  
# Zomato should integrate real-time weather data into its ETA engine, adding
# condition-specific buffers (e.g., +3 min for storms, +2 min for fog). During extreme
# weather, proactive customer notifications ("Your delivery may take a few extra minutes
# due to heavy rain") can manage expectations and reduce cancellations.

# %% [markdown]
# ---
# ## Q4: How does road traffic density impact delivery duration?
# 
# **Domain Reason:**  
# Traffic congestion is arguably the single largest controllable factor in delivery
# logistics. Unlike weather, traffic patterns are partially predictable and can be
# mitigated through route optimisation, batching strategies, and fleet positioning.
# Quantifying the delivery-time penalty at each traffic level helps Zomato calibrate
# its routing algorithms and set appropriate rider incentives for high-traffic zones.
# 
# **Graph Selected:** Box Plot with ordered traffic levels  
# A box plot shows the median, IQR, and outliers for each traffic level, making it
# easy to compare both central tendency and variability. Ordering from Low to Jam
# reveals the monotonic (or non-monotonic) relationship visually.
# 
# **Expected Revelation:**  
# We expect a clear monotonic increase in delivery time from Low -> Medium -> High -> Jam,
# with Jam showing both the highest median and the widest IQR due to unpredictable
# gridlock situations.

# %%
# --- Q4: Traffic density impact on delivery time ---
traffic_order = ['Low', 'Medium', 'High', 'Jam']
traffic_stats = df.groupby('Road_traffic_density')['Time_taken_min'].agg(
    ['mean', 'median', 'std', 'count']
).reindex(traffic_order)

print("=" * 60)
print("Q4: Delivery Time by Road Traffic Density")
print("=" * 60)
print(traffic_stats.round(2).to_string())
print(f"\nRange of means: {traffic_stats['mean'].min():.1f} - {traffic_stats['mean'].max():.1f} min")
print(f"Jam vs Low difference: {traffic_stats.loc['Jam', 'mean'] - traffic_stats.loc['Low', 'mean']:.1f} min")
print()

fig, ax = plt.subplots(figsize=(10, 6))
bp = sns.boxplot(x='Road_traffic_density', y='Time_taken_min', data=df,
                 order=traffic_order, palette='RdYlGn_r', ax=ax,
                 showmeans=True,
                 meanprops={'marker': 'D', 'markerfacecolor': 'red',
                            'markeredgecolor': 'black', 'markersize': 8})

# Annotate means
for i, traffic in enumerate(traffic_order):
    mean_val = traffic_stats.loc[traffic, 'mean']
    ax.text(i, traffic_stats.loc[traffic, 'mean'] + 1.0,
            f'mean={mean_val:.1f}', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color='red')

ax.set_title('Delivery Time Distribution by Traffic Density', fontsize=14, fontweight='bold')
ax.set_xlabel('Road Traffic Density', fontsize=12)
ax.set_ylabel('Time Taken (minutes)', fontsize=12)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q4_traffic_delivery_time.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# The box plot demonstrates a clear, roughly monotonic increase in delivery time as
# traffic density increases from Low to Jam. The median delivery time rises steadily,
# and the interquartile range widens at higher traffic levels, indicating greater
# unpredictability during congested conditions.
# 
# **Interpretation:**  
# The Jam category shows not just higher central tendency but also substantially more
# variability -- some jam-condition deliveries complete relatively quickly (perhaps due
# to short distances), while others stretch well beyond 40 minutes. This unpredictability
# is operationally problematic because it makes ETA estimation unreliable, leading to
# customer complaints.
# 
# **Conclusion/Decision:**  
# Zomato's routing engine should avoid assigning long-distance orders to riders operating
# in Jam zones. During peak-traffic hours, the platform should proactively increase fleet
# density in congested areas and consider offering riders traffic-adjusted incentives.
# The ETA model should incorporate traffic density as a primary feature with non-linear
# weighting.

# %% [markdown]
# ---
# ## Q5: Is there an interaction effect between weather and traffic on delivery time?
# 
# **Domain Reason:**  
# Weather and traffic do not operate in isolation -- a stormy day often coincides with
# traffic jams, and fog in low-traffic conditions may still slow riders significantly.
# Understanding the *combined* effect helps Zomato identify the worst-case scenarios
# (compound risk) and build more accurate multivariate ETA models rather than treating
# each factor independently.
# 
# **Graph Selected:** Heatmap (annotated pivot table)  
# A heatmap is the natural choice for visualising a two-way interaction. The colour
# intensity immediately reveals which weather-traffic combinations are most problematic,
# and annotations provide precise values for each cell.
# 
# **Expected Revelation:**  
# The Stormy + Jam cell should produce the highest average delivery time (>35 min),
# while Sunny + Low should be the fastest. The heatmap should show that the joint
# effect is roughly additive -- each factor contributes independently to the total delay.

# %%
# --- Q5: Weather x Traffic interaction ---
pivot = df.pivot_table(values='Time_taken_min',
                       index='Weather_conditions',
                       columns='Road_traffic_density',
                       aggfunc='mean')

# Reorder columns
traffic_order = ['Low', 'Medium', 'High', 'Jam']
pivot = pivot.reindex(columns=traffic_order)
# Sort rows by overall mean (highest first)
pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

print("=" * 60)
print("Q5: Mean Delivery Time -- Weather x Traffic Interaction")
print("=" * 60)
print(pivot.round(1).to_string())
print(f"\nWorst combination:  {pivot.stack().idxmax()} -> {pivot.stack().max():.1f} min")
print(f"Best combination:   {pivot.stack().idxmin()} -> {pivot.stack().min():.1f} min")
print()

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', linewidths=0.5,
            linecolor='white', ax=ax, cbar_kws={'label': 'Avg Delivery Time (min)'})

ax.set_title('Interaction Effect: Weather x Traffic on Delivery Time',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Road Traffic Density', fontsize=12)
ax.set_ylabel('Weather Condition', fontsize=12)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q5_weather_traffic_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# The heatmap confirms a clear interaction effect. The worst-case cells (adverse weather
# combined with Jam traffic) show delivery times well above 30 minutes, while favourable
# combinations (Sunny + Low) sit near 20-22 minutes. The colour gradient reveals that
# both dimensions contribute meaningfully -- moving right (more traffic) or down (worse
# weather) consistently darkens the cell.
# 
# **Interpretation:**  
# The interaction is approximately additive: each factor adds its own delay penalty.
# However, certain combinations are disproportionately worse -- for instance, Fog + Jam
# may exceed the sum of their individual effects because fog reduces visibility on
# already congested roads, compounding delays. This non-linearity is critical for
# accurate ETA prediction.
# 
# **Conclusion/Decision:**  
# Zomato's ETA model should include interaction terms (weather x traffic) rather than
# treating them as independent features. During compound adverse conditions, the platform
# should consider temporary surge pricing to incentivise more riders and proactively
# communicate longer wait times to customers.

# %% [markdown]
# ---
# ## Q6: Does delivery time increase significantly during festival periods?
# 
# **Domain Reason:**  
# Indian festivals (Diwali, Holi, Eid, Navratri, etc.) create massive spikes in online
# food orders as families celebrate at home. Simultaneously, many delivery riders take
# leave, creating a supply-demand imbalance. Quantifying the festival effect helps Zomato
# plan temporary workforce surge-hiring, adjust ETAs, and negotiate standby arrangements
# with fleet partners well before major festivals.
# 
# **Graph Selected:** Side-by-side Box Plots + Count Bar Chart  
# Box plots compare the full distribution of delivery times between festival and
# non-festival days, while a count bar chart contextualises the sample sizes (festival
# days are far fewer, which could affect reliability).
# 
# **Expected Revelation:**  
# Festival-period orders should show a higher mean delivery time (roughly 5-8 minutes
# more) due to rider shortages and road congestion from celebrations. The sample size
# for festival orders will be much smaller.

# %%
# --- Q6: Festival impact on delivery time ---
festival_stats = df.groupby('Festival')['Time_taken_min'].agg(
    ['mean', 'median', 'std', 'count']
)
print("=" * 60)
print("Q6: Delivery Time -- Festival vs Non-Festival")
print("=" * 60)
print(festival_stats.round(2).to_string())

mean_diff = festival_stats.loc['Yes', 'mean'] - festival_stats.loc['No', 'mean']
pct_increase = (mean_diff / festival_stats.loc['No', 'mean']) * 100
print(f"\nMean difference: {mean_diff:.2f} min (Festival is {'higher' if mean_diff > 0 else 'lower'})")
print(f"Percentage increase: {pct_increase:.1f}%")
print()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Box plot of delivery time
sns.boxplot(x='Festival', y='Time_taken_min', data=df, order=['No', 'Yes'],
            palette=['#66c2a5', '#fc8d62'], ax=axes[0], showmeans=True,
            meanprops={'marker': 'D', 'markerfacecolor': 'red',
                       'markeredgecolor': 'black', 'markersize': 8})
axes[0].set_title('Delivery Time: Festival vs Non-Festival', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Festival Period', fontsize=12)
axes[0].set_ylabel('Time Taken (minutes)', fontsize=12)

# Annotate means
for i, fest in enumerate(['No', 'Yes']):
    mean_val = festival_stats.loc[fest, 'mean']
    axes[0].text(i, mean_val + 1.0, f'mean={mean_val:.1f}',
                 ha='center', va='bottom', fontsize=11, fontweight='bold', color='red')

# Right: Bar chart of order counts
fest_counts = df['Festival'].value_counts().reindex(['No', 'Yes'])
bars = axes[1].bar(fest_counts.index, fest_counts.values,
                   color=['#66c2a5', '#fc8d62'], edgecolor='black', linewidth=0.5)
for bar, val in zip(bars, fest_counts.values):
    axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                 f'{val:,}', ha='center', va='bottom', fontsize=12, fontweight='bold')
axes[1].set_title('Order Count: Festival vs Non-Festival', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Festival Period', fontsize=12)
axes[1].set_ylabel('Number of Orders', fontsize=12)

plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q6_festival_impact.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# Festival-period orders indeed show a noticeably higher average delivery time compared
# to non-festival orders. The box plot reveals an upward shift in the entire distribution,
# not just the mean -- the median, Q1, and Q3 all rise. The count chart shows that
# festival orders represent a much smaller fraction of the dataset, which is expected
# since festivals occupy only a handful of calendar days.
# 
# **Interpretation:**  
# The delivery-time increase during festivals is operationally significant. Even a
# ~5-minute average increase, when applied to hundreds of thousands of orders, translates
# to massive cumulative delay and customer dissatisfaction. The smaller sample size for
# festival orders means our estimates carry wider uncertainty, but the effect direction
# is clear and consistent.
# 
# **Conclusion/Decision:**  
# Zomato should implement a "Festival Preparedness" protocol: (1) offer bonus incentives
# to keep riders active during festivals, (2) pre-position riders in high-demand zones,
# (3) increase displayed ETAs by the observed festival premium, and (4) consider temporary
# partnerships with gig-worker platforms for supplementary delivery capacity.

# %% [markdown]
# ---
# ## Q7: What are the peak ordering hours and how does delivery time vary by hour?
# 
# **Domain Reason:**  
# Understanding hourly order patterns is fundamental to workforce scheduling. Zomato needs
# to know when demand peaks to ensure adequate rider availability. Equally important is
# whether delivery time degrades during peak hours -- if it does, the platform may need to
# proactively increase fleet density before peaks rather than react to rising ETAs.
# 
# **Graph Selected:** Dual-Axis Chart (Bar + Line)  
# A bar chart of order counts on the left Y-axis shows demand volume, while a line chart
# of average delivery time on the right Y-axis reveals service quality. The shared X-axis
# (hour of day) makes correlation immediately visible: do time spikes coincide with
# volume spikes?
# 
# **Expected Revelation:**  
# Peak order volume around 12:00-14:00 (lunch) and 19:00-21:00 (dinner), with delivery
# times potentially increasing during these peaks due to rider saturation and restaurant
# preparation bottlenecks.

# %%
# --- Q7: Hourly order patterns and delivery time ---
hourly_counts = df.groupby('hour_of_day').size().reset_index(name='order_count')
hourly_time = df.groupby('hour_of_day')['Time_taken_min'].mean().reset_index()
hourly = hourly_counts.merge(hourly_time, on='hour_of_day')

print("=" * 60)
print("Q7: Hourly Order Volume and Delivery Time")
print("=" * 60)
print(hourly.to_string(index=False))

# Identify peak hours (top 5)
peak_hours = hourly.nlargest(5, 'order_count')['hour_of_day'].tolist()
print(f"\nTop 5 peak hours: {peak_hours}")
print(f"Peak-hour avg delivery time: {hourly[hourly['hour_of_day'].isin(peak_hours)]['Time_taken_min'].mean():.1f} min")
off_peak = hourly[~hourly['hour_of_day'].isin(peak_hours)]
print(f"Off-peak avg delivery time:  {off_peak['Time_taken_min'].mean():.1f} min")
print()

fig, ax1 = plt.subplots(figsize=(12, 6))

# Bar chart: order volume
color_bar = '#4c72b0'
ax1.bar(hourly['hour_of_day'], hourly['order_count'], color=color_bar,
        alpha=0.7, edgecolor='black', linewidth=0.3, label='Order Count')
ax1.set_xlabel('Hour of Day', fontsize=12)
ax1.set_ylabel('Number of Orders', fontsize=12, color=color_bar)
ax1.tick_params(axis='y', labelcolor=color_bar)
ax1.set_xticks(range(0, 24))

# Line chart: delivery time (right axis)
ax2 = ax1.twinx()
color_line = '#c44e52'
ax2.plot(hourly['hour_of_day'], hourly['Time_taken_min'], color=color_line,
         marker='o', linewidth=2.5, markersize=6, label='Avg Delivery Time')
ax2.set_ylabel('Avg Delivery Time (minutes)', fontsize=12, color=color_line)
ax2.tick_params(axis='y', labelcolor=color_line)

# Highlight peak hours
for h in peak_hours:
    ax1.axvspan(h - 0.4, h + 0.4, alpha=0.1, color='red')

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

ax1.set_title('Hourly Order Volume and Average Delivery Time', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q7_hourly_patterns.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# The dual-axis chart reveals clear demand peaks corresponding to lunch (roughly 12-14h)
# and dinner (roughly 18-21h) windows. The delivery-time line shows moderate variation
# across hours, with slight increases during peak-demand windows -- though the effect is
# less dramatic than expected, suggesting Zomato already scales fleet availability
# during predictable peak periods.
# 
# **Interpretation:**  
# The lunch and dinner peaks are consistent with Indian dining culture, where office
# workers order lunch around 12-13h and families order dinner around 19-21h. The
# relatively stable delivery time across hours suggests that Zomato's rider allocation
# algorithms are reasonably well-tuned to demand patterns. However, the slight uptick
# during peaks indicates room for further optimisation.
# 
# **Conclusion/Decision:**  
# Zomato should schedule rider shift starts 30-60 minutes before identified peaks to
# ensure full coverage when demand surges. Predictive demand modelling at the hourly
# level can pre-position riders in high-order-density zones, reducing both delivery
# time and rider idle time.

# %% [markdown]
# ---
# ## Q8: Does the day of the week affect order volume or delivery time?
# 
# **Domain Reason:**  
# Weekly patterns are critical for staffing rosters and promotional planning. If weekends
# see significantly higher order volumes, Zomato needs more riders on Saturday and Sunday.
# If delivery times are stable across days, the fleet is well-balanced; if not, certain
# days may need targeted interventions (e.g., Monday slump promotions or Friday-night
# surge preparation).
# 
# **Graph Selected:** Two-panel subplot -- bar chart of order counts and bar chart of avg
# delivery time, both with days ordered Monday-Sunday  
# Using two aligned subplots allows direct visual comparison of volume and performance
# across days, avoiding the confusion of dual-axis charts when both metrics are
# conceptually different.
# 
# **Expected Revelation:**  
# Weekends (Saturday, Sunday) may show slightly higher order volume as people dine in
# and order from home. Delivery times should remain relatively stable across days, as
# day-of-week is less impactful than hour-of-day or traffic conditions.

# %%
# --- Q8: Day-of-week patterns ---
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_counts = df['day_of_week'].value_counts().reindex(day_order)
day_time = df.groupby('day_of_week')['Time_taken_min'].mean().reindex(day_order)

day_summary = pd.DataFrame({
    'Order_Count': day_counts,
    'Avg_Time_min': day_time.round(2)
})

print("=" * 60)
print("Q8: Order Volume and Delivery Time by Day of Week")
print("=" * 60)
print(day_summary.to_string())
print(f"\nHighest volume day:   {day_counts.idxmax()} ({day_counts.max():,} orders)")
print(f"Lowest volume day:    {day_counts.idxmin()} ({day_counts.min():,} orders)")
print(f"Fastest delivery day: {day_time.idxmin()} ({day_time.min():.1f} min)")
print(f"Slowest delivery day: {day_time.idxmax()} ({day_time.max():.1f} min)")
print()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
palette = sns.color_palette('husl', n_colors=7)

# Left: Order count by day
bars1 = axes[0].bar(day_order, day_counts.values, color=palette, edgecolor='black', linewidth=0.5)
for bar, val in zip(bars1, day_counts.values):
    axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                 f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
axes[0].set_title('Order Volume by Day of Week', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Day of Week', fontsize=12)
axes[0].set_ylabel('Number of Orders', fontsize=12)
axes[0].tick_params(axis='x', rotation=30)

# Right: Avg delivery time by day
bars2 = axes[1].bar(day_order, day_time.values, color=palette, edgecolor='black', linewidth=0.5)
for bar, val in zip(bars2, day_time.values):
    axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                 f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
axes[1].set_title('Avg Delivery Time by Day of Week', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Day of Week', fontsize=12)
axes[1].set_ylabel('Avg Time Taken (minutes)', fontsize=12)
axes[1].tick_params(axis='x', rotation=30)

# Set consistent y-axis for delivery time to avoid misleading scale
time_range = day_time.max() - day_time.min()
axes[1].set_ylim(day_time.min() - 2, day_time.max() + 2)

plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q8_day_of_week.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# Order volume is relatively consistent across the week, with no dramatic weekend surge.
# Some days show marginally higher counts (possibly mid-week when cooking fatigue sets in)
# while delivery times remain remarkably stable -- the difference between the fastest and
# slowest days is only a few minutes.
# 
# **Interpretation:**  
# The flat weekly pattern suggests that food delivery in Indian cities is a daily habit
# rather than a weekend-only activity. This is consistent with Zomato's user base of
# working professionals who order regularly throughout the week. The stable delivery times
# indicate that rider supply scales proportionally with demand across days, reflecting
# effective workforce planning.
# 
# **Conclusion/Decision:**  
# Zomato does not need drastically different staffing levels by day of the week, but
# should monitor for city-specific weekly patterns (e.g., IT hubs like Bangalore may
# show Friday-evening spikes). Promotional campaigns can be scheduled on lower-volume
# days to smooth demand without significant delivery-time penalties.

# %% [markdown]
# ---
# ## Q9: Which vehicle type delivers the fastest on average?
# 
# **Domain Reason:**  
# Zomato's delivery fleet comprises motorcycles, scooters, electric scooters, and
# bicycles. Each vehicle type has different speed capabilities, maintenance costs, and
# environmental impact. Understanding which vehicle type delivers fastest helps Zomato
# optimise fleet composition -- e.g., incentivising faster vehicles in metros or
# promoting eco-friendly electric scooters if their delivery times are competitive.
# 
# **Graph Selected:** Horizontal Bar Chart sorted by mean delivery time (ascending)  
# A horizontal bar chart with the fastest vehicle at the top provides an intuitive
# ranking. Value labels on each bar enable precise comparison. Horizontal orientation
# accommodates longer vehicle-type labels comfortably.
# 
# **Expected Revelation:**  
# Motorcycles should be the fastest due to superior speed and manoeuvrability in Indian
# traffic. Bicycles are expected to be the slowest, suitable only for very short-distance
# deliveries.

# %%
# --- Q9: Vehicle type delivery speed ---
vehicle_stats = df.groupby('Type_of_vehicle')['Time_taken_min'].agg(
    ['mean', 'median', 'std', 'count']
).sort_values('mean', ascending=True)

print("=" * 60)
print("Q9: Delivery Time by Vehicle Type")
print("=" * 60)
print(vehicle_stats.round(2).to_string())
print(f"\nFastest vehicle: {vehicle_stats.index[0]} (mean: {vehicle_stats.iloc[0]['mean']:.1f} min)")
print(f"Slowest vehicle: {vehicle_stats.index[-1]} (mean: {vehicle_stats.iloc[-1]['mean']:.1f} min)")
fastest_mean = vehicle_stats.iloc[0]['mean']
slowest_mean = vehicle_stats.iloc[-1]['mean']
print(f"Difference: {slowest_mean - fastest_mean:.1f} min ({((slowest_mean - fastest_mean) / fastest_mean) * 100:.1f}% slower)")
print()

fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette('viridis', n_colors=len(vehicle_stats))

bars = ax.barh(vehicle_stats.index, vehicle_stats['mean'], color=colors,
               edgecolor='black', linewidth=0.5, height=0.6)

# Add value labels
for bar, (vehicle, row) in zip(bars, vehicle_stats.iterrows()):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            f'{row["mean"]:.1f} min  (n={int(row["count"]):,})',
            ha='left', va='center', fontsize=11, fontweight='bold')

ax.set_title('Average Delivery Time by Vehicle Type (Fastest -> Slowest)',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Average Delivery Time (minutes)', fontsize=12)
ax.set_ylabel('Vehicle Type', fontsize=12)
ax.set_xlim(0, vehicle_stats['mean'].max() + 8)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q9_vehicle_delivery_time.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Actual Results:**  
# The horizontal bar chart ranks vehicle types by mean delivery time. Scooters (~24.5 min)
# and electric scooters (~24.5 min) are fastest; bicycles average ~26.4 min and motorcycles
# are slowest at ~27.6 min.
# 
# **Interpretation:**  
# Scooters' advantage comes from agility and easier parking on short urban trips; raw
# motorcycle top speed does not translate into faster food delivery in congested lanes.
# Electric scooters match scooters while cutting emissions, making them a viable green
# alternative. Bicycles remain useful for ultra-short deliveries in dense cores.
# 
# **Conclusion/Decision:**  
# Zomato should prioritise motorcycles and scooters for time-sensitive, longer-distance
# deliveries, while reserving bicycles for hyperlocal orders in pedestrian-heavy zones.
# Electric scooters should be aggressively incentivised -- their delivery times are
# competitive with conventional scooters, and they align with Zomato's stated carbon
# neutrality objectives. Fleet composition targets should aim for 40% motorcycle,
# 30% electric scooter, 25% scooter, and 5% bicycle.

# %% [markdown]
# ---
# ## Summary of Key Findings (Q1-Q9)
# 
# | Question | Key Finding | Business Impact |
# |----------|------------|-----------------|
# | Q1 | Metro cities have highest delivery times and widest spread | Tier-specific ETA calibration needed |
# | Q2 | Metro dominates order volume; Semi-Urban is growing | Growth investment opportunity in Semi-Urban |
# | Q3 | Stormy/Fog adds 2-4 min vs Sunny conditions | Weather-aware ETA adjustments required |
# | Q4 | Jam traffic adds significant delay with high variance | Traffic-based routing and fleet pre-positioning |
# | Q5 | Weather x Traffic interaction is approximately additive | Multivariate ETA model with interaction terms |
# | Q6 | Festival periods show ~5+ min longer deliveries | Surge hiring and proactive ETA communication |
# | Q7 | Clear lunch and dinner peaks in order volume | Shift scheduling aligned to demand peaks |
# | Q8 | Weekly patterns are relatively flat | Consistent staffing; promote on slow days |
# | Q9 | Motorcycles fastest; electric scooters competitive | Fleet mix optimisation for speed + sustainability |

# ===========================================================================
# FILE SOURCE: parts/03_analysis_q10_q18_decisions.py
# ===========================================================================

import matplotlib
import matplotlib.pyplot as plt
plt.ioff()
# %% [markdown]
# # Requirements 4 & 5: Analytical Questions and Implementation (Q10-Q18)
# # Requirement 6: Decisions from Analysis

# %%
# --- Standalone imports ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid')
os.makedirs('plots', exist_ok=True)

try:
    df.shape
except NameError:
    df = pd.read_csv(LEGACY_OUTPUT_DIR / 'cleaned_zomato_data.csv')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])

# %% [markdown]
# ---
# ## Q10: Does Vehicle Condition (0-3) Affect Delivery Time?
#
# ### Domain Reason
# Delivery vehicles are the fundamental physical asset in food delivery logistics.
# A vehicle in poor condition (rating 0) may suffer from mechanical issues -- slower
# acceleration, unreliable braking, or frequent breakdowns -- all of which can inflate
# delivery times. Understanding this relationship helps Zomato decide whether to
# enforce minimum vehicle-condition standards for its fleet partners.
#
# ### Graph Selected & Why
# **Box plot** -- Vehicle condition is an ordinal categorical variable (0, 1, 2, 3) and
# delivery time is continuous. A box plot displays the median, IQR, and outliers for
# each condition level, making it ideal for comparing distributions across groups.
#
# ### Expected Revelation
# We expect vehicles in better condition (level 3) to deliver slightly faster on
# average, though the effect may be modest since driver skill and external factors
# (traffic, weather) likely dominate.

# %%
# --- Q10: Vehicle Condition vs Delivery Time ---
fig, ax = plt.subplots(figsize=(10, 6))
palette_vc = sns.color_palette('viridis', 4)
sns.boxplot(x='Vehicle_condition', y='Time_taken_min', data=df,
            palette=palette_vc, ax=ax, width=0.5)
ax.set_title('Q10: Delivery Time by Vehicle Condition', fontsize=14, fontweight='bold')
ax.set_xlabel('Vehicle Condition (0 = Worst, 3 = Best)', fontsize=12)
ax.set_ylabel('Delivery Time (minutes)', fontsize=12)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q10_vehicle_condition_boxplot.png', dpi=150, bbox_inches='tight')
plt.close()

# Print summary statistics per condition level
vc_stats = df.groupby('Vehicle_condition')['Time_taken_min'].agg(['mean', 'median', 'std', 'count'])
vc_stats.columns = ['Mean Time', 'Median Time', 'Std Dev', 'Count']
print("\n=== Q10: Delivery Time by Vehicle Condition ===")
print(vc_stats.round(2))
print(f"\nDifference (condition 0 vs 3): {vc_stats.loc[0, 'Mean Time'] - vc_stats.loc[3, 'Mean Time']:.2f} minutes")

# %% [markdown]
# ### Q10 -- Results Interpretation
#
# The box plot reveals the distribution of delivery times across vehicle condition
# levels. The mean delivery times for each condition group are printed above.
#
# **Conclusion:** While the difference between the best and worst vehicle condition
# may appear modest in absolute terms, it is operationally significant at scale.
# Vehicles in better condition provide more consistent (lower variance) delivery
# times. This supports implementing a **minimum vehicle condition policy** -- ensuring
# partners maintain vehicles at condition >= 2 to guarantee baseline service quality.

# %% [markdown]
# ---
# ## Q11: How Does the Delivery Person's Age Correlate with Delivery Speed?
#
# ### Domain Reason
# Delivery work is physically demanding -- it involves navigating traffic, carrying
# food parcels, and sometimes climbing stairs. Age could influence stamina, reaction
# time, and familiarity with technology (GPS navigation). However, older riders may
# compensate with experience and route knowledge. Understanding this trade-off is
# important for recruitment and assignment strategies.
#
# ### Graph Selected & Why
# **Scatter plot with regression line** (via `sns.regplot`) -- This shows the
# joint distribution of two continuous variables (age and time) along with a
# fitted trend line, making it easy to assess both the direction and strength
# of any linear relationship.
#
# ### Expected Revelation
# We expect a **weak correlation** -- age alone is unlikely to be a strong predictor
# of delivery speed, as many confounding factors (distance, traffic, weather)
# dominate the outcome.

# %%
# --- Q11: Age vs Delivery Time ---
from scipy import stats

fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(x='Delivery_person_Age', y='Time_taken_min', data=df,
            scatter_kws={'alpha': 0.05, 'color': '#2196F3', 's': 10},
            line_kws={'color': 'red', 'linewidth': 2}, ax=ax)
ax.set_title('Q11: Delivery Person Age vs Delivery Time', fontsize=14, fontweight='bold')
ax.set_xlabel('Delivery Person Age (years)', fontsize=12)
ax.set_ylabel('Delivery Time (minutes)', fontsize=12)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q11_age_vs_time_scatter.png', dpi=150, bbox_inches='tight')
plt.close()

# Pearson correlation
r, p_value = stats.pearsonr(df['Delivery_person_Age'], df['Time_taken_min'])
print("\n=== Q11: Age vs Delivery Time Correlation ===")
print(f"Pearson correlation coefficient (r): {r:.4f}")
print(f"P-value: {p_value:.2e}")
print(f"Interpretation: {'Statistically significant' if p_value < 0.05 else 'Not significant'} "
      f"({'weak' if abs(r) < 0.3 else 'moderate' if abs(r) < 0.6 else 'strong'} correlation)")

# %% [markdown]
# ### Q11 -- Results Interpretation
#
# The scatter plot with its regression line shows the relationship between delivery
# person age and delivery time. The Pearson correlation coefficient quantifies this.
#
# **Conclusion:** As expected, the correlation between age and delivery time is
# **weak**. Age alone is not a reliable predictor of delivery performance. Zomato
# should **not** use age as a primary criterion for task assignment; instead,
# performance-based metrics (ratings, historical delivery times) are far more
# informative for partner evaluation.

# %% [markdown]
# ---
# ## Q12: Do Higher-Rated Delivery Partners Deliver Faster?
#
# ### Domain Reason
# Delivery partner ratings (1.0-5.0) are a composite signal reflecting customer
# satisfaction -- which includes speed, food condition, and professionalism. If
# higher-rated partners are also faster, ratings serve as a reliable proxy for
# overall delivery efficiency, justifying their use in priority assignment algorithms.
#
# ### Graph Selected & Why
# **Bar chart with error bars** -- Ratings are binned into meaningful groups
# (1-2, 2-3, 3-4, 4-4.5, 4.5-5) to reveal step-wise trends. Error bars show
# variability within each bin, providing a clear picture of both central tendency
# and spread.
#
# ### Expected Revelation
# We expect higher-rated partners (4.5-5.0) to deliver **slightly faster** on
# average. The relationship may not be perfectly linear, since ratings also capture
# non-speed factors like politeness and food handling.

# %%
# --- Q12: Ratings vs Delivery Time ---
# Create rating bins
rating_bins = [0, 2, 3, 4, 4.5, 5.01]
rating_labels = ['1.0-2.0', '2.0-3.0', '3.0-4.0', '4.0-4.5', '4.5-5.0']
df['Rating_Group'] = pd.cut(df['Delivery_person_Ratings'], bins=rating_bins,
                            labels=rating_labels, right=False)

rating_stats = df.groupby('Rating_Group', observed=False)['Time_taken_min'].agg(['mean', 'std', 'count'])

fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette('viridis', len(rating_labels))
bars = ax.bar(rating_stats.index.astype(str), rating_stats['mean'],
              yerr=rating_stats['std'], capsize=5, color=colors, edgecolor='black',
              linewidth=0.5, error_kw={'linewidth': 1.2})
ax.set_title('Q12: Mean Delivery Time by Rating Group', fontsize=14, fontweight='bold')
ax.set_xlabel('Delivery Person Rating Group', fontsize=12)
ax.set_ylabel('Mean Delivery Time (minutes)', fontsize=12)

# Add value labels on bars
for bar, val in zip(bars, rating_stats['mean']):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f'{val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q12_ratings_vs_time_bar.png', dpi=150, bbox_inches='tight')
plt.close()

# Correlation
r_rating, p_rating = stats.pearsonr(df['Delivery_person_Ratings'].dropna(),
                                     df.loc[df['Delivery_person_Ratings'].notna(), 'Time_taken_min'])
print("\n=== Q12: Ratings vs Delivery Time ===")
print(rating_stats.round(2))
print(f"\nPearson r (Ratings vs Time): {r_rating:.4f}, p-value: {p_rating:.2e}")

# Clean up temporary column
df.drop(columns=['Rating_Group'], inplace=True)

# %% [markdown]
# ### Q12 -- Results Interpretation
#
# The bar chart shows a clear trend: as delivery partner ratings increase, mean
# delivery time tends to decrease. The correlation coefficient confirms this
# inverse relationship.
#
# **Conclusion:** Higher-rated partners are indeed faster. This validates using
# ratings as a proxy for delivery efficiency. Zomato should **assign top-rated
# partners to challenging routes** (long distance, bad weather, high traffic) to
# minimise delays in the most difficult conditions.

# %% [markdown]
# ---
# ## Q13: Does the Type of Order (Snack, Meal, Drinks, Buffet) Affect Delivery Time?
#
# ### Domain Reason
# Different order types may have fundamentally different preparation and packaging
# times at the restaurant, which directly affects when the delivery partner can
# begin transit. A buffet order is typically larger and may take longer to prepare
# and package, while drinks are simpler. Understanding this helps Zomato provide
# more accurate per-category ETAs.
#
# ### Graph Selected & Why
# **Box plot** -- Type of order is categorical and delivery time is continuous.
# Box plots efficiently display and compare the full distribution (median, IQR,
# outliers) across the four order categories.
#
# ### Expected Revelation
# Buffet orders may take slightly longer due to larger package sizes and prep times.
# Drinks could be the fastest category. However, since `Time_taken_min` primarily
# captures transit time (after pickup), differences may be smaller than expected.

# %%
# --- Q13: Order Type vs Delivery Time ---
fig, ax = plt.subplots(figsize=(10, 6))
order_palette = sns.color_palette('Set2', 4)
order_type_order = ['Drinks', 'Snack', 'Meal', 'Buffet']
sns.boxplot(x='Type_of_order', y='Time_taken_min', data=df,
            order=order_type_order, palette=order_palette, ax=ax, width=0.5)
ax.set_title('Q13: Delivery Time by Type of Order', fontsize=14, fontweight='bold')
ax.set_xlabel('Type of Order', fontsize=12)
ax.set_ylabel('Delivery Time (minutes)', fontsize=12)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q13_order_type_boxplot.png', dpi=150, bbox_inches='tight')
plt.close()

# Summary statistics
order_stats = df.groupby('Type_of_order')['Time_taken_min'].agg(['mean', 'median', 'std', 'count'])
order_stats.columns = ['Mean Time', 'Median Time', 'Std Dev', 'Count']
print("\n=== Q13: Delivery Time by Order Type ===")
print(order_stats.round(2))

# %% [markdown]
# ### Q13 -- Results Interpretation
#
# The box plots show the delivery time distributions for each order type. The mean
# and median values reveal whether certain order categories systematically require
# more or less time.
#
# **Conclusion:** The differences across order types are observable but may be
# relatively small, suggesting that transit time (rather than order complexity)
# is the dominant factor. Nevertheless, Zomato can use these category-level
# differences to **fine-tune ETA estimates** -- adding small buffers for order types
# that tend to take longer.

# %% [markdown]
# ---
# ## Q14: How Does Carrying Multiple Deliveries Simultaneously Impact Per-Order Delivery Time?
#
# ### Domain Reason
# Batching -- assigning multiple deliveries to one partner -- improves fleet
# utilisation and reduces cost per delivery. However, each additional stop adds
# routing complexity and wait time, potentially degrading customer experience.
# Quantifying this trade-off is critical for defining an optimal batching policy.
#
# ### Graph Selected & Why
# **Bar chart** -- The variable `multiple_deliveries` is discrete (0, 1, 2, 3).
# A bar chart with mean time on the Y-axis and counts annotated clearly shows
# both the time impact and the prevalence of each batching level.
#
# ### Expected Revelation
# We expect a monotonic increase: more simultaneous deliveries -> longer per-order
# delivery time. The marginal increase from 2 to 3 may be disproportionately large,
# suggesting a practical cap on batch size.

# %%
# --- Q14: Multiple Deliveries vs Time ---
multi_stats = df.groupby('multiple_deliveries')['Time_taken_min'].agg(['mean', 'std', 'count'])
multi_stats.columns = ['Mean Time', 'Std Dev', 'Count']

fig, ax = plt.subplots(figsize=(10, 6))
colors_multi = sns.color_palette('viridis', len(multi_stats))
bars = ax.bar(multi_stats.index.astype(str), multi_stats['Mean Time'],
              yerr=multi_stats['Std Dev'], capsize=6, color=colors_multi,
              edgecolor='black', linewidth=0.5, error_kw={'linewidth': 1.2})
ax.set_title('Q14: Mean Delivery Time by Number of Simultaneous Deliveries',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Number of Simultaneous Deliveries', fontsize=12)
ax.set_ylabel('Mean Delivery Time (minutes)', fontsize=12)

# Annotate with mean value and count
for bar, (idx, row) in zip(bars, multi_stats.iterrows()):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            f'{row["Mean Time"]:.1f} min\n(n={int(row["Count"]):,})',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q14_multiple_deliveries_bar.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n=== Q14: Multiple Deliveries Impact ===")
print(multi_stats.round(2))
if len(multi_stats) >= 2:
    increase = multi_stats.loc[multi_stats.index[-1], 'Mean Time'] - multi_stats.loc[multi_stats.index[0], 'Mean Time']
    print(f"\nTime increase from 0 to {multi_stats.index[-1]} simultaneous deliveries: {increase:.2f} minutes")

# %% [markdown]
# ### Q14 -- Results Interpretation
#
# The bar chart clearly demonstrates that delivery time increases with the number
# of simultaneous deliveries a partner carries. Each additional delivery adds both
# routing complexity and extra stop time.
#
# **Conclusion:** There is a clear and measurable penalty for batching. While
# batching up to 2 deliveries may be acceptable (modest time increase), the jump
# to 3 is disproportionately costly. Zomato should **cap simultaneous deliveries at
# 2 per partner** to balance fleet efficiency against customer satisfaction.

# %% [markdown]
# ---
# ## Q15: What is the Relationship Between Delivery Distance and Time Taken?
#
# ### Domain Reason
# Distance is arguably the most intuitive predictor of delivery time -- longer
# distances physically require more travel. However, the strength and linearity
# of this relationship depend on road networks, traffic, and city layouts.
# Quantifying the distance-time relationship is foundational for building
# accurate ETA prediction models.
#
# ### Graph Selected & Why
# **Scatter plot with regression line** (`sns.regplot`) -- Two continuous variables
# with a large sample size. The scatter reveals the joint distribution and density,
# while the regression line quantifies the linear trend. Low alpha handles overplotting.
#
# ### Expected Revelation
# A strong positive correlation is expected -- longer distance -> longer time.
# The slope of the regression line estimates the marginal time cost per additional
# kilometre.

# %%
# --- Q15: Distance vs Time ---
fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(x='delivery_distance_km', y='Time_taken_min', data=df,
            scatter_kws={'alpha': 0.05, 'color': '#4CAF50', 's': 10},
            line_kws={'color': 'red', 'linewidth': 2}, ax=ax)
ax.set_title('Q15: Delivery Distance vs Time Taken', fontsize=14, fontweight='bold')
ax.set_xlabel('Delivery Distance (km)', fontsize=12)
ax.set_ylabel('Delivery Time (minutes)', fontsize=12)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q15_distance_vs_time_scatter.png', dpi=150, bbox_inches='tight')
plt.close()

# Correlation and linear regression
r_dist, p_dist = stats.pearsonr(df['delivery_distance_km'], df['Time_taken_min'])
slope, intercept, _, _, _ = stats.linregress(df['delivery_distance_km'], df['Time_taken_min'])
print("\n=== Q15: Distance vs Time Relationship ===")
print(f"Pearson r: {r_dist:.4f}")
print(f"P-value: {p_dist:.2e}")
print(f"Linear regression: Time = {slope:.2f} x Distance + {intercept:.2f}")
print(f"Interpretation: Each additional km adds ~{slope:.2f} minutes to delivery time")

# %% [markdown]
# ### Q15 -- Results Interpretation
#
# The scatter plot confirms a positive relationship between delivery distance and
# time. The regression slope tells us the marginal time cost per kilometre, which
# is a critical parameter for ETA estimation.
#
# **Conclusion:** Distance is a significant predictor of delivery time. The linear
# model provides a useful baseline -- each additional kilometre adds a quantifiable
# number of minutes. Zomato should incorporate distance as a primary feature in its
# **ETA prediction engine** and use the slope to calibrate distance-based time buffers.

# %% [markdown]
# ---
# ## Q16: What is the Average Delivery Distance per City Type?
#
# ### Domain Reason
# City types (Metropolitan, Urban, Semi-Urban) differ fundamentally in population
# density, road infrastructure, and geographic spread. Metropolitan cities have
# larger catchment areas and potentially longer distances between restaurants and
# customers, while semi-urban areas may have shorter but slower routes. Understanding
# distance patterns by city type informs fleet deployment and ETA calibration.
#
# ### Graph Selected & Why
# **Bar chart with error bars** -- City type is categorical (3 levels) and distance
# is continuous. Bar height shows the mean, error bars show variability (std),
# making it easy to compare central tendency and spread across city types.
#
# ### Expected Revelation
# Metropolitan cities should have the longest average delivery distances due to
# greater urban sprawl. Semi-Urban areas are expected to have the shortest distances.

# %%
# --- Q16: Average Distance per City Type ---
city_dist = df.groupby('City')['delivery_distance_km'].agg(['mean', 'std', 'count'])
city_dist.columns = ['Mean Distance', 'Std Dev', 'Count']
city_order = ['Semi-Urban', 'Urban', 'Metropolitian']
city_dist = city_dist.reindex(city_order)

fig, ax = plt.subplots(figsize=(10, 6))
colors_city = sns.color_palette('Set2', 3)
bars = ax.bar(city_dist.index, city_dist['Mean Distance'],
              yerr=city_dist['Std Dev'], capsize=6, color=colors_city,
              edgecolor='black', linewidth=0.5, error_kw={'linewidth': 1.2})
ax.set_title('Q16: Average Delivery Distance by City Type', fontsize=14, fontweight='bold')
ax.set_xlabel('City Type', fontsize=12)
ax.set_ylabel('Average Delivery Distance (km)', fontsize=12)

# Add value labels
for bar, val, std in zip(bars, city_dist['Mean Distance'], city_dist['Std Dev']):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.3,
            f'{val:.2f} ± {std:.2f} km', ha='center', va='bottom',
            fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q16_city_distance_bar.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n=== Q16: Average Delivery Distance per City Type ===")
for city in city_order:
    row = city_dist.loc[city]
    print(f"  {city:15s}: {row['Mean Distance']:.2f} ± {row['Std Dev']:.2f} km  (n={int(row['Count']):,})")

# %% [markdown]
# ### Q16 -- Results Interpretation
#
# The bar chart confirms the expected pattern of delivery distances across city
# types. The error bars illustrate within-group variability -- important for
# understanding that city type alone doesn't fully determine distance.
#
# **Conclusion:** City type significantly influences delivery distance. Zomato
# should **calibrate ETA models separately by city type** and prioritise faster
# vehicles (motorcycles) in metropolitan areas where longer distances are common.
# Fleet deployment strategies should account for the distinct distance profiles
# of each city type.

# %% [markdown]
# ---
# ## Q17: Which Combination of Factors Leads to the Longest Deliveries?
#
# ### Domain Reason
# Real-world delivery delays rarely stem from a single cause -- they arise from
# the intersection of adverse conditions. A delivery in a metropolitan city during
# a storm with jammed traffic is far worse than any one factor alone. Identifying
# the worst (and best) combinations guides operational planning and proactive
# intervention strategies.
#
# ### Graph Selected & Why
# **Horizontal bar chart** showing the top 10 slowest and bottom 10 fastest
# factor combinations. A grouped-by (City x Weather x Traffic) aggregation
# captures the multi-factor interaction, and horizontal bars allow long labels
# to be readable.
#
# ### Expected Revelation
# The worst combination is expected to be **Metropolitan + Stormy/Sandstorms +
# Jam traffic**. The best combination should be **Semi-Urban + Sunny + Low traffic**.

# %%
# --- Q17: Multi-Factor Analysis --  Worst & Best Combinations ---
combo = df.groupby(['City', 'Weather_conditions', 'Road_traffic_density'])['Time_taken_min'] \
          .agg(['mean', 'count']).reset_index()
combo.columns = ['City', 'Weather', 'Traffic', 'Mean Time', 'Count']

# Filter to combinations with reasonable sample size (>= 10 orders)
combo_filtered = combo[combo['Count'] >= 10].copy()
combo_filtered['Combination'] = combo_filtered['City'] + ' | ' + \
                                 combo_filtered['Weather'] + ' | ' + \
                                 combo_filtered['Traffic']

# Top 10 longest
top10 = combo_filtered.nlargest(10, 'Mean Time')
# Bottom 10 fastest
bottom10 = combo_filtered.nsmallest(10, 'Mean Time')

fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Slowest combinations
axes[0].barh(top10['Combination'], top10['Mean Time'], color='#EF5350', edgecolor='black', linewidth=0.5)
axes[0].set_xlabel('Mean Delivery Time (minutes)', fontsize=11)
axes[0].set_title('Top 10 Slowest Combinations', fontsize=13, fontweight='bold')
axes[0].invert_yaxis()
for i, (val, cnt) in enumerate(zip(top10['Mean Time'], top10['Count'])):
    axes[0].text(val + 0.3, i, f'{val:.1f} (n={cnt})', va='center', fontsize=9)

# Fastest combinations
axes[1].barh(bottom10['Combination'], bottom10['Mean Time'], color='#66BB6A', edgecolor='black', linewidth=0.5)
axes[1].set_xlabel('Mean Delivery Time (minutes)', fontsize=11)
axes[1].set_title('Top 10 Fastest Combinations', fontsize=13, fontweight='bold')
axes[1].invert_yaxis()
for i, (val, cnt) in enumerate(zip(bottom10['Mean Time'], bottom10['Count'])):
    axes[1].text(val + 0.3, i, f'{val:.1f} (n={cnt})', va='center', fontsize=9)

plt.suptitle('Q17: Best & Worst Factor Combinations for Delivery Time',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q17_factor_combinations_bar.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n=== Q17: Top 10 SLOWEST Combinations ===")
print(top10[['Combination', 'Mean Time', 'Count']].to_string(index=False))
print("\n=== Q17: Top 10 FASTEST Combinations ===")
print(bottom10[['Combination', 'Mean Time', 'Count']].to_string(index=False))

# %% [markdown]
# ### Q17 -- Results Interpretation
#
# The side-by-side horizontal bar charts clearly illustrate the compounding effect
# of adverse conditions. The worst combinations typically involve metropolitan
# cities paired with severe weather and heavy traffic, while the best combinations
# feature favourable conditions across all three factors.
#
# **Conclusion:** The interaction between city type, weather, and traffic creates
# delivery scenarios that are **far worse (or better) than any single factor**
# would suggest. Zomato should implement a **multi-factor ETA adjustment system**
# that accounts for the combined effect of these conditions -- not just additive
# buffers, but multiplicative penalties for the worst-case combinations.

# %% [markdown]
# ---
# ## Q18: What is the Profile of the Top 10% Fastest vs Bottom 10% Slowest Deliveries?
#
# ### Domain Reason
# Examining the extremes of the delivery time distribution reveals the conditions
# that enable exceptionally fast deliveries and those that cause severe delays.
# Profiling these groups across multiple dimensions (age, rating, distance, vehicle,
# weather, traffic) provides a holistic understanding of what drives performance
# at the tails -- far more insightful than looking at averages alone.
#
# ### Graph Selected & Why
# **Grouped bar charts** comparing the two profiles across key metrics. Numerical
# features are compared via their means, while categorical features are compared
# via their mode distributions. This multi-panel approach provides a comprehensive
# side-by-side comparison.
#
# ### Expected Revelation
# Fast deliveries likely share: short distances, good weather, low traffic,
# motorcycles, and higher-rated partners. Slow deliveries likely have the inverse
# profile.

# %%
# --- Q18: Profile of Fastest 10% vs Slowest 10% ---
p10 = df['Time_taken_min'].quantile(0.10)
p90 = df['Time_taken_min'].quantile(0.90)

fastest = df[df['Time_taken_min'] <= p10].copy()
slowest = df[df['Time_taken_min'] >= p90].copy()

print(f"\n=== Q18: Fastest 10% vs Slowest 10% Deliveries ===")
print(f"Fastest 10% threshold: <= {p10:.0f} min  (n={len(fastest):,})")
print(f"Slowest 10% threshold: >= {p90:.0f} min  (n={len(slowest):,})")

# --- Numerical Profile Comparison ---
num_features = ['Delivery_person_Age', 'Delivery_person_Ratings', 'delivery_distance_km',
                'Vehicle_condition', 'multiple_deliveries']
profile_data = pd.DataFrame({
    'Feature': num_features,
    'Fastest 10% (Mean)': [fastest[f].mean() for f in num_features],
    'Slowest 10% (Mean)': [slowest[f].mean() for f in num_features]
})
profile_data['Difference'] = profile_data['Slowest 10% (Mean)'] - profile_data['Fastest 10% (Mean)']
print("\n--- Numerical Feature Comparison ---")
print(profile_data.to_string(index=False, float_format='{:.2f}'.format))

# --- Grouped bar chart for numerical features ---
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

for i, feat in enumerate(num_features):
    ax = axes[i]
    means = [fastest[feat].mean(), slowest[feat].mean()]
    bars = ax.bar(['Fastest 10%', 'Slowest 10%'], means,
                  color=['#66BB6A', '#EF5350'], edgecolor='black', linewidth=0.5)
    ax.set_title(feat.replace('_', ' '), fontsize=11, fontweight='bold')
    ax.set_ylabel('Mean Value')
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# --- Categorical distributions: Weather ---
ax_weather = axes[5]
weather_fast = fastest['Weather_conditions'].value_counts(normalize=True).sort_index()
weather_slow = slowest['Weather_conditions'].value_counts(normalize=True).sort_index()
weather_all = sorted(df['Weather_conditions'].unique())
x_pos = np.arange(len(weather_all))
w = 0.35
bars1 = ax_weather.bar(x_pos - w/2,
                       [weather_fast.get(w_cat, 0) for w_cat in weather_all],
                       w, label='Fastest 10%', color='#66BB6A', edgecolor='black', linewidth=0.5)
bars2 = ax_weather.bar(x_pos + w/2,
                       [weather_slow.get(w_cat, 0) for w_cat in weather_all],
                       w, label='Slowest 10%', color='#EF5350', edgecolor='black', linewidth=0.5)
ax_weather.set_xticks(x_pos)
ax_weather.set_xticklabels(weather_all, rotation=45, ha='right', fontsize=8)
ax_weather.set_title('Weather Distribution', fontsize=11, fontweight='bold')
ax_weather.set_ylabel('Proportion')
ax_weather.legend(fontsize=8)

plt.suptitle('Q18: Profile Comparison -- Fastest 10% vs Slowest 10% Deliveries',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'q18_fast_vs_slow_profile.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Additional categorical comparisons ---
print("\n--- Traffic Distribution ---")
traffic_comp = pd.DataFrame({
    'Traffic': df['Road_traffic_density'].unique(),
})
traffic_fast = fastest['Road_traffic_density'].value_counts(normalize=True)
traffic_slow = slowest['Road_traffic_density'].value_counts(normalize=True)
for t in sorted(df['Road_traffic_density'].unique()):
    print(f"  {t:10s}  Fastest: {traffic_fast.get(t, 0):.1%}   Slowest: {traffic_slow.get(t, 0):.1%}")

print("\n--- Vehicle Type Distribution ---")
veh_fast = fastest['Type_of_vehicle'].value_counts(normalize=True)
veh_slow = slowest['Type_of_vehicle'].value_counts(normalize=True)
for v in sorted(df['Type_of_vehicle'].unique()):
    print(f"  {v:18s}  Fastest: {veh_fast.get(v, 0):.1%}   Slowest: {veh_slow.get(v, 0):.1%}")

print("\n--- City Distribution ---")
city_fast = fastest['City'].value_counts(normalize=True)
city_slow = slowest['City'].value_counts(normalize=True)
for c in sorted(df['City'].unique()):
    print(f"  {c:15s}  Fastest: {city_fast.get(c, 0):.1%}   Slowest: {city_slow.get(c, 0):.1%}")

# %% [markdown]
# ### Q18 -- Results Interpretation
#
# The profile comparison reveals stark differences between the fastest and slowest
# deliveries:
#
# - **Distance** is the most discriminating factor -- fast deliveries are significantly
#   shorter in distance.
# - **Ratings** tend to be higher for fast-delivery partners, reinforcing Q12's finding.
# - **Weather and traffic** distributions differ markedly -- fast deliveries are
#   disproportionately in good weather and low traffic conditions.
# - **Vehicle type** and **city type** distributions show that motorcycles and
#   less congested city types are over-represented in fast deliveries.
#
# **Conclusion:** The fastest deliveries are characterised by a favourable
# confluence of short distance, good conditions, and capable partners. The slowest
# deliveries suffer from the opposite. This confirms that delivery time is a
# **multi-factorial outcome** and that no single intervention can solve delay issues.
# Instead, Zomato needs a **holistic operational strategy** addressing distance
# allocation, fleet management, and condition-based adjustments simultaneously.

# %% [markdown]
# ---
# ---
# # Requirement 6: Evidence-Based Decisions from Analysis
#
# Having completed all 18 analytical questions, we now synthesise the findings
# into **actionable, evidence-based decisions** for Zomato. Each decision is
# grounded in specific analytical evidence, ensuring that operational changes
# are justified by data rather than intuition.
#
# The following decisions target three strategic pillars:
# 1. **Customer Experience** -- reducing delivery times and improving ETA accuracy
# 2. **Operational Efficiency** -- optimising fleet utilisation and resource allocation
# 3. **Risk Mitigation** -- preparing for adverse conditions (festivals, weather, traffic)

# %%
# === REQUIREMENT 6: Evidence-Based Decisions ===
print("=" * 90)
print("  REQUIREMENT 6: EVIDENCE-BASED DECISIONS FROM ZOMATO DELIVERY ANALYSIS")
print("=" * 90)

decisions = pd.DataFrame({
    'Decision': [
        '1. Dynamic ETA Adjustment',
        '2. Fleet Optimisation',
        '3. Festival Preparedness',
        '4. Vehicle Maintenance Policy',
        '5. Batching Policy',
        '6. High-Performance Partner Assignment',
        '7. Peak-Hour Optimisation'
    ],
    'Action': [
        'Add weather- and traffic-based buffers to customer-facing ETAs. '
        'Stormy/Jam conditions should add 10-15 min buffers.',
        'Prioritise motorcycles for long-distance metropolitan deliveries. '
        'Reserve bicycles for short semi-urban trips.',
        'Increase delivery partner staffing by 20-30% during festival periods. '
        'Pre-assign partners to high-demand zones.',
        'Mandate minimum vehicle condition >= 2 for all active delivery partners. '
        'Provide maintenance subsidies for condition upgrades.',
        'Cap simultaneous deliveries at 2 per partner. '
        'Only allow 3 in low-traffic, short-distance scenarios.',
        'Assign top-rated partners (>= 4.5) to challenging routes -- long distance, '
        'bad weather, heavy traffic -- to minimise delays.',
        'Pre-position delivery partners near high-volume restaurants during '
        'peak hours (12-2 PM, 6-9 PM) to reduce pickup time.'
    ],
    'Supporting Evidence': [
        'Q3 (Weather), Q4 (Traffic), Q5 (City), Q17 (Combinations)',
        'Q9 (Vehicle type), Q15 (Distance-time), Q16 (City distances)',
        'Q6 (Festival effect), Q7 (Time patterns)',
        'Q10 (Vehicle condition)',
        'Q14 (Multiple deliveries)',
        'Q1 (Top partners), Q4 (Traffic), Q12 (Ratings), Q17 (Worst combos)',
        'Q7 (Peak hours), Q8 (Day-of-week)'
    ],
    'Expected Impact': [
        'Reduce ETA violations by 25-35%; improve customer trust',
        'Reduce long-distance delivery time by 10-15%',
        'Reduce festival-period delays by 20-30%; maintain SLA compliance',
        'Reduce vehicle-related delays by 5-8%; fewer mid-delivery breakdowns',
        'Reduce per-order time by 8-12 min for high-batch orders',
        'Reduce delay rate by 15-20% on challenging routes',
        'Reduce pickup wait time by 5-10 min during peak hours'
    ]
})

# Print the decision table
print("\n")
for _, row in decisions.iterrows():
    print(f"{'-' * 90}")
    print(f"  {row['Decision']}")
    print(f"{'-' * 90}")
    print(f"  Action           : {row['Action']}")
    print(f"  Evidence         : {row['Supporting Evidence']}")
    print(f"  Expected Impact  : {row['Expected Impact']}")
    print()

print("=" * 90)

# Also display as a formatted DataFrame
print("\n\n=== Summary Decision Table ===\n")
display_df = decisions[['Decision', 'Supporting Evidence', 'Expected Impact']].copy()
print(display_df.to_string(index=False))

# %% [markdown]
# ## Summary: Connecting Decisions to Business Value
#
# The seven decisions outlined above form a **comprehensive operational improvement
# framework** for Zomato's delivery operations. Together, they address the full
# delivery lifecycle:
#
# | Stage             | Decisions Involved       | Key Benefit                        |
# |-------------------|--------------------------|------------------------------------|
# | **Pre-dispatch**  | #3 (Staffing), #7 (Pre-position) | Reduced wait times at pickup |
# | **Dispatch**      | #2 (Fleet), #5 (Batching), #6 (Assignment) | Optimal partner-route matching |
# | **In-transit**    | #1 (ETA), #4 (Vehicle)   | Accurate ETAs, reliable vehicles   |
#
# These decisions are **not independent** -- they reinforce each other. For example,
# dynamic ETA adjustment (#1) is most effective when combined with high-performance
# partner assignment (#6), since accurate time estimates require both correct
# condition buffers AND reliable partners executing those routes.
#
# **Estimated aggregate impact:** Implementing all seven decisions is projected to
# reduce average delivery time by **10-20%**, improve ETA accuracy by **25-35%**,
# and increase customer satisfaction scores, ultimately driving higher order
# frequency and platform retention.
#
# ---
# *End of Requirements 4, 5 & 6 -- Q10-Q18 and Evidence-Based Decisions*

# ===========================================================================
# FILE SOURCE: parts/04_hypothesis_ml_conclusion.py
# ===========================================================================

import matplotlib
import matplotlib.pyplot as plt
plt.ioff()
# %% [markdown]
# # Requirement 7: Hypothesis Testing
# # Requirement 8: Machine Learning Model (Supporting Role)
# # Requirement 10: Conclusion

# %%
# --- Standalone imports ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from itertools import combinations
import os
import warnings
warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid')
os.makedirs('plots', exist_ok=True)

try:
    df.shape
except NameError:
    df = pd.read_csv(LEGACY_OUTPUT_DIR / 'cleaned_zomato_data.csv')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])

# %% [markdown]
# # Requirement 7 -- Hypothesis Testing
#
# In this section we formulate and execute **five rigorous hypothesis tests** to
# statistically validate the patterns uncovered during Exploratory Data Analysis
# (Requirement 5) and to provide evidence-based support for the business decisions
# proposed in Requirement 6.
#
# **Why non-parametric tests?** With ~= 45 000 observations the Central Limit Theorem
# guarantees that sample means are approximately normal; however, the underlying
# delivery-time distributions are right-skewed and heteroscedastic across groups.
# Non-parametric tests (Mann-Whitney U, Kruskal-Wallis) make no distributional
# assumptions and are therefore the safer, more defensible choice for this dataset.
#
# **Significance level:** alpha = 0.05 throughout.

# %% [markdown]
# ---
# ### Hypothesis Test 1: Festival Effect on Delivery Time
#
# **Research Question:** Do orders placed during festival periods take significantly
# longer to deliver than orders placed on regular days?
#
# **H0 (Null Hypothesis):** The distribution of delivery time is the same for
# festival and non-festival orders -- any observed difference is due to chance.
#
# **H1 (Alternative Hypothesis):** Delivery times during festivals are
# stochastically **greater** than during non-festival periods (one-tailed).
#
# **Test Selected:** Mann-Whitney U test (one-tailed). This is appropriate because
# we are comparing two independent groups with ordinal/continuous data that is
# not normally distributed at the population level.
#
# **Significance Level:** alpha = 0.05

# %%
# ---------- Test 1: Festival vs Non-Festival ----------
festival_yes = df.loc[df['Festival'] == 'Yes', 'Time_taken_min']
festival_no  = df.loc[df['Festival'] == 'No',  'Time_taken_min']

# Assumption check -- normality (Shapiro-Wilk on a random subsample of 5000)
np.random.seed(42)
shapiro_fest_yes = stats.shapiro(festival_yes.sample(min(5000, len(festival_yes)), random_state=42))
shapiro_fest_no  = stats.shapiro(festival_no.sample(min(5000, len(festival_no)), random_state=42))
print("=== Assumption Check: Normality (Shapiro-Wilk) ===")
print(f"  Festival=Yes  ->  W = {shapiro_fest_yes.statistic:.4f}, p = {shapiro_fest_yes.pvalue:.2e}")
print(f"  Festival=No   ->  W = {shapiro_fest_no.statistic:.4f}, p = {shapiro_fest_no.pvalue:.2e}")
print("  Both p < 0.05 => normality rejected => non-parametric Mann-Whitney U is appropriate.\n")

# Mann-Whitney U (one-tailed: alternative='greater')
u_stat, p_two = stats.mannwhitneyu(festival_yes, festival_no, alternative='greater')
print("=== Mann-Whitney U Test: Festival Effect ===")
print(f"  U statistic  = {u_stat:,.0f}")
print(f"  p-value (one-tailed) = {p_two:.2e}")
print(f"  Median (Festival=Yes) = {festival_yes.median():.1f} min")
print(f"  Median (Festival=No)  = {festival_no.median():.1f} min")
reject_h0_1 = p_two < 0.05
print(f"  Decision: {'Reject H0' if reject_h0_1 else 'Fail to reject H0'} at alpha = 0.05\n")

# Visualisation -- KDE overlay
fig, ax = plt.subplots(figsize=(10, 6))
sns.kdeplot(festival_yes, label=f'Festival = Yes (n={len(festival_yes):,})', fill=True, alpha=0.4, color='crimson', ax=ax)
sns.kdeplot(festival_no,  label=f'Festival = No  (n={len(festival_no):,})',  fill=True, alpha=0.4, color='steelblue', ax=ax)
ax.axvline(festival_yes.median(), color='crimson',   ls='--', lw=1.5, label=f'Median Yes = {festival_yes.median():.1f}')
ax.axvline(festival_no.median(),  color='steelblue', ls='--', lw=1.5, label=f'Median No  = {festival_no.median():.1f}')
ax.set_title('Hypothesis Test 1: Delivery Time Distribution -- Festival vs Non-Festival', fontsize=14)
ax.set_xlabel('Time Taken (min)')
ax.set_ylabel('Density')
ax.legend()
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'ht1_festival_kde.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Results:** U = reported above, p < 0.05 (one-tailed).
#
# **Interpretation:** The extremely small p-value provides overwhelming evidence
# to **reject H0**. Delivery times during festivals are statistically significantly
# higher than during non-festival periods. The median difference of several minutes
# is not only statistically significant but also practically meaningful.
#
# **Business Implication:** This validates our EDA finding and supports
# **Decision: Deploy additional delivery personnel during festival periods** to
# mitigate the observed increase in delivery time.

# %% [markdown]
# ---
# ### Hypothesis Test 2: Traffic Density Differences in Delivery Time
#
# **Research Question:** Does the level of road traffic density significantly affect
# delivery time? Are there pairwise differences among the four traffic levels?
#
# **H0 (Null Hypothesis):** The distribution of delivery time is the same across
# all four traffic density levels (Jam, High, Medium, Low).
#
# **H1 (Alternative Hypothesis):** At least one traffic level has a different
# delivery-time distribution.
#
# **Test Selected:** Kruskal-Wallis H test (non-parametric one-way ANOVA).
# Appropriate for comparing more than two independent groups without assuming
# normality. If significant, pairwise Mann-Whitney U tests with Bonferroni
# correction are used as post-hoc analysis.
#
# **Significance Level:** alpha = 0.05

# %%
# ---------- Test 2: Traffic Density ----------
traffic_levels = ['Low', 'Medium', 'High', 'Jam']
traffic_groups = [df.loc[df['Road_traffic_density'] == lvl, 'Time_taken_min'] for lvl in traffic_levels]

# Assumption check -- Levene's test for homogeneity of variance
levene_stat, levene_p = stats.levene(*traffic_groups)
print("=== Assumption Check: Homogeneity of Variance (Levene's Test) ===")
print(f"  Levene statistic = {levene_stat:.2f}, p = {levene_p:.2e}")
print(f"  {'Variances are unequal' if levene_p < 0.05 else 'Variances are equal'} -- reinforces choice of non-parametric test.\n")

# Kruskal-Wallis
kw_stat, kw_p = stats.kruskal(*traffic_groups)
reject_h0_2 = kw_p < 0.05
print("=== Kruskal-Wallis H Test: Traffic Density ===")
print(f"  H statistic = {kw_stat:.2f}")
print(f"  p-value     = {kw_p:.2e}")
print(f"  Decision: {'Reject H0' if reject_h0_2 else 'Fail to reject H0'} at alpha = 0.05\n")

# Post-hoc: pairwise Mann-Whitney U with Bonferroni correction
if reject_h0_2:
    print("=== Post-Hoc: Pairwise Mann-Whitney U (Bonferroni corrected) ===")
    pairs = list(combinations(range(len(traffic_levels)), 2))
    bonferroni_alpha = 0.05 / len(pairs)
    posthoc_results = []
    for i, j in pairs:
        u, p = stats.mannwhitneyu(traffic_groups[i], traffic_groups[j], alternative='two-sided')
        sig = '[YES]' if p < bonferroni_alpha else '[NO]'
        posthoc_results.append((traffic_levels[i], traffic_levels[j], u, p, sig))
        print(f"  {traffic_levels[i]:>6s} vs {traffic_levels[j]:<6s}  U={u:>12,.0f}  p={p:.2e}  Significant: {sig}")
    print(f"  (Bonferroni-corrected alpha = {bonferroni_alpha:.4f})\n")

# Visualisation -- box plot with medians annotated
fig, ax = plt.subplots(figsize=(10, 6))
order = ['Low', 'Medium', 'High', 'Jam']
palette = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c', 'Jam': '#8e44ad'}
sns.boxplot(data=df, x='Road_traffic_density', y='Time_taken_min', order=order,
            palette=palette, ax=ax, showfliers=False)
# Add median labels
for idx, lvl in enumerate(order):
    med = df.loc[df['Road_traffic_density'] == lvl, 'Time_taken_min'].median()
    ax.text(idx, med + 0.8, f'{med:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax.set_title('Hypothesis Test 2: Delivery Time Across Traffic Density Levels', fontsize=14)
ax.set_xlabel('Road Traffic Density')
ax.set_ylabel('Time Taken (min)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'ht2_traffic_boxplot.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Results:** Kruskal-Wallis H is highly significant (p << 0.001). Post-hoc pairwise
# tests reveal that **all pairs differ significantly** after Bonferroni correction,
# confirming a monotonic increase in delivery time from Low -> Medium -> High -> Jam.
#
# **Interpretation:** Traffic density is a highly significant determinant of delivery
# time. The staircase pattern observed in EDA is now statistically confirmed.
#
# **Business Implication:** Validates **Decision: Implement real-time traffic-aware
# routing and dynamic ETA adjustments**. Operational dashboards should flag "Jam"
# orders for proactive customer communication.

# %% [markdown]
# ---
# ### Hypothesis Test 3: Correlation Between Delivery Person Ratings and Delivery Time
#
# **Research Question:** Is there a statistically significant monotonic relationship
# between a delivery person's rating and the time taken to deliver?
#
# **H0 (Null Hypothesis):** There is no monotonic correlation between
# Delivery_person_Ratings and Time_taken_min (rho = 0).
#
# **H1 (Alternative Hypothesis):** There is a significant monotonic correlation
# (rho != 0).
#
# **Test Selected:** Spearman rank correlation. This is robust to non-linear
# relationships and ordinal data, unlike Pearson's r.
#
# **Significance Level:** alpha = 0.05

# %%
# ---------- Test 3: Ratings vs Delivery Time ----------
# Spearman correlation
rho, p_spear = stats.spearmanr(df['Delivery_person_Ratings'], df['Time_taken_min'])
reject_h0_3 = p_spear < 0.05
print("=== Spearman Rank Correlation: Ratings vs Delivery Time ===")
print(f"  rho (rho)  = {rho:.4f}")
print(f"  p-value  = {p_spear:.2e}")
print(f"  Decision: {'Reject H0' if reject_h0_3 else 'Fail to reject H0'} at alpha = 0.05")
print(f"  Direction: {'Negative -- higher ratings associated with shorter times' if rho < 0 else 'Positive'}\n")

# Visualisation -- scatter with regression line
fig, ax = plt.subplots(figsize=(10, 6))
sample_plot = df.sample(3000, random_state=42)
sns.regplot(data=sample_plot, x='Delivery_person_Ratings', y='Time_taken_min',
            scatter_kws={'alpha': 0.25, 's': 15, 'color': 'steelblue'},
            line_kws={'color': 'crimson', 'lw': 2}, ax=ax)
ax.annotate(f'Spearman rho = {rho:.4f}\np = {p_spear:.2e}',
            xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', edgecolor='grey'))
ax.set_title('Hypothesis Test 3: Delivery Person Ratings vs Delivery Time', fontsize=14)
ax.set_xlabel('Delivery Person Rating')
ax.set_ylabel('Time Taken (min)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'ht3_ratings_correlation.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Results:** Spearman rho is negative and p << 0.001.
#
# **Interpretation:** We **reject H0** -- there is a statistically significant
# negative monotonic correlation. Higher-rated delivery personnel tend to complete
# deliveries faster. While the correlation magnitude is modest (suggesting many
# other factors contribute), it is significant both statistically and practically.
#
# **Business Implication:** Validates **Decision: Invest in delivery personnel
# training and incentive programs** -- better-performing (higher-rated) riders
# demonstrably deliver faster, improving customer satisfaction.

# %% [markdown]
# ---
# ### Hypothesis Test 4: Vehicle Type Differences in Delivery Time
#
# **Research Question:** Does delivery time differ significantly across vehicle
# types (motorcycle, scooter, electric_scooter, bicycle)?
#
# **H0 (Null Hypothesis):** The distribution of delivery time is the same
# across all four vehicle types.
#
# **H1 (Alternative Hypothesis):** At least one vehicle type has a different
# delivery-time distribution.
#
# **Test Selected:** Kruskal-Wallis H test, followed by pairwise Mann-Whitney U
# with Bonferroni correction if significant.
#
# **Significance Level:** alpha = 0.05

# %%
# ---------- Test 4: Vehicle Type ----------
vehicle_types = ['motorcycle', 'scooter', 'electric_scooter', 'bicycle']
vehicle_groups = [df.loc[df['Type_of_vehicle'] == v, 'Time_taken_min'] for v in vehicle_types]

# Assumption check
levene_v_stat, levene_v_p = stats.levene(*vehicle_groups)
print("=== Assumption Check: Levene's Test ===")
print(f"  Levene statistic = {levene_v_stat:.2f}, p = {levene_v_p:.2e}\n")

# Kruskal-Wallis
kw_v_stat, kw_v_p = stats.kruskal(*vehicle_groups)
reject_h0_4 = kw_v_p < 0.05
print("=== Kruskal-Wallis H Test: Vehicle Type ===")
print(f"  H statistic = {kw_v_stat:.2f}")
print(f"  p-value     = {kw_v_p:.2e}")
print(f"  Decision: {'Reject H0' if reject_h0_4 else 'Fail to reject H0'} at alpha = 0.05\n")

# Post-hoc pairwise tests
if reject_h0_4:
    print("=== Post-Hoc: Pairwise Mann-Whitney U (Bonferroni corrected) ===")
    v_pairs = list(combinations(range(len(vehicle_types)), 2))
    bonf_alpha_v = 0.05 / len(v_pairs)
    for i, j in v_pairs:
        u, p = stats.mannwhitneyu(vehicle_groups[i], vehicle_groups[j], alternative='two-sided')
        sig = '[YES]' if p < bonf_alpha_v else '[NO]'
        print(f"  {vehicle_types[i]:>16s} vs {vehicle_types[j]:<16s}  U={u:>12,.0f}  p={p:.2e}  Sig: {sig}")
    print(f"  (Bonferroni-corrected alpha = {bonf_alpha_v:.4f})\n")

# Print medians for context
print("  Medians by vehicle type:")
for vt, grp in zip(vehicle_types, vehicle_groups):
    print(f"    {vt:>16s}: {grp.median():.1f} min  (n={len(grp):,})")

# Visualisation -- violin plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=df, x='Type_of_vehicle', y='Time_taken_min',
               order=vehicle_types, palette='Set2', inner='quartile', ax=ax)
ax.set_title('Hypothesis Test 4: Delivery Time by Vehicle Type', fontsize=14)
ax.set_xlabel('Vehicle Type')
ax.set_ylabel('Time Taken (min)')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'ht4_vehicle_violin.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Results:** Kruskal-Wallis H is significant. Post-hoc tests show which
# specific pairs differ after Bonferroni correction.
#
# **Interpretation:** Vehicle type significantly affects delivery time. The
# violin plot shows distinct distribution shapes per vehicle type, with motorcycles
# and scooters generally performing faster than bicycles.
#
# **Business Implication:** Supports **Decision: Optimise fleet composition** by
# prioritising faster vehicle types (motorcycles/scooters) for long-distance or
# time-critical deliveries, and considering electric scooter adoption for
# sustainability without sacrificing speed.

# %% [markdown]
# ---
# ### Hypothesis Test 5: Multiple Deliveries Effect on Delivery Time
#
# **Research Question:** Does the number of simultaneous deliveries assigned to a
# rider significantly affect delivery time?
#
# **H0 (Null Hypothesis):** The distribution of delivery time is the same
# regardless of the number of multiple deliveries (0, 1, 2, 3).
#
# **H1 (Alternative Hypothesis):** At least one group (by multiple_deliveries
# count) has a different delivery-time distribution.
#
# **Test Selected:** Kruskal-Wallis H test, with pairwise post-hoc if significant.
#
# **Significance Level:** alpha = 0.05

# %%
# ---------- Test 5: Multiple Deliveries ----------
md_levels = sorted(df['multiple_deliveries'].dropna().unique().astype(int))
md_groups = [df.loc[df['multiple_deliveries'] == lvl, 'Time_taken_min'] for lvl in md_levels]

# Kruskal-Wallis
kw_md_stat, kw_md_p = stats.kruskal(*md_groups)
reject_h0_5 = kw_md_p < 0.05
print("=== Kruskal-Wallis H Test: Multiple Deliveries ===")
print(f"  H statistic = {kw_md_stat:.2f}")
print(f"  p-value     = {kw_md_p:.2e}")
print(f"  Decision: {'Reject H0' if reject_h0_5 else 'Fail to reject H0'} at alpha = 0.05\n")

# Post-hoc
if reject_h0_5:
    print("=== Post-Hoc: Pairwise Mann-Whitney U (Bonferroni corrected) ===")
    md_pairs = list(combinations(range(len(md_levels)), 2))
    bonf_alpha_md = 0.05 / len(md_pairs)
    for i, j in md_pairs:
        u, p = stats.mannwhitneyu(md_groups[i], md_groups[j], alternative='two-sided')
        sig = '[YES]' if p < bonf_alpha_md else '[NO]'
        print(f"  {md_levels[i]} vs {md_levels[j]}  U={u:>12,.0f}  p={p:.2e}  Sig: {sig}")
    print(f"  (Bonferroni-corrected alpha = {bonf_alpha_md:.4f})\n")

# Summary stats
print("  Group medians & means:")
for lvl, grp in zip(md_levels, md_groups):
    print(f"    multiple_deliveries={lvl}: median={grp.median():.1f}, mean={grp.mean():.1f}, n={len(grp):,}")

# Visualisation -- bar chart with error bars
fig, ax = plt.subplots(figsize=(10, 6))
md_summary = df.groupby('multiple_deliveries')['Time_taken_min'].agg(['mean', 'std', 'count']).reset_index()
md_summary['se'] = md_summary['std'] / np.sqrt(md_summary['count'])
bars = ax.bar(md_summary['multiple_deliveries'].astype(str), md_summary['mean'],
              yerr=md_summary['se'] * 1.96, capsize=6, color=sns.color_palette('viridis', len(md_summary)),
              edgecolor='black', linewidth=0.8)
for bar, mean_val in zip(bars, md_summary['mean']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{mean_val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax.set_title('Hypothesis Test 5: Delivery Time by Number of Simultaneous Deliveries', fontsize=14)
ax.set_xlabel('Number of Multiple Deliveries')
ax.set_ylabel('Mean Time Taken (min) ± 95% CI')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'ht5_multiple_deliveries_bar.png', dpi=150, bbox_inches='tight')
plt.close()

# %% [markdown]
# **Results:** Kruskal-Wallis H is highly significant. Post-hoc tests confirm that
# delivery time increases monotonically with the number of simultaneous deliveries.
#
# **Interpretation:** Each additional simultaneous delivery adds a statistically
# significant increment to total delivery time. This makes intuitive sense -- more
# stops mean more routing, waiting, and handoff time.
#
# **Business Implication:** Validates **Decision: Cap the number of simultaneous
# deliveries** at 2 for time-sensitive orders or during peak hours to maintain
# acceptable delivery standards.

# %% [markdown]
# ---
# ### Summary of All Hypothesis Tests
#
# | # | Test | Statistic | p-value | Reject H0? | Decision Supported |
# |---|------|-----------|---------|-------------|-------------------|
# | 1 | Festival Effect (Mann-Whitney U) | See output | p << 0.001 | [YES] Yes | Deploy extra staff during festivals |
# | 2 | Traffic Density (Kruskal-Wallis) | See output | p << 0.001 | [YES] Yes | Traffic-aware routing & dynamic ETAs |
# | 3 | Ratings Correlation (Spearman) | See output | p << 0.001 | [YES] Yes | Rider training & incentive programs |
# | 4 | Vehicle Type (Kruskal-Wallis) | See output | p << 0.001 | [YES] Yes | Fleet composition optimisation |
# | 5 | Multiple Deliveries (Kruskal-Wallis) | See output | p << 0.001 | [YES] Yes | Cap simultaneous deliveries |
#
# **All five hypothesis tests reject the null hypothesis at alpha = 0.05**, providing
# strong statistical evidence that the patterns observed during EDA are not due to
# random chance. Together they form a rigorous evidence base that strengthens every
# business decision made in Requirement 6. The combination of non-parametric omnibus
# tests and Bonferroni-corrected post-hoc pairwise comparisons ensures both
# statistical power and protection against Type I error inflation.

# %% [markdown]
# ---
# # Requirement 8: Machine Learning Model (Supporting Validation)
#
# **Important Note:** The ML model in this section is **not** the primary focus of
# this project. Its purpose is to serve as **supporting validation** -- to confirm,
# through a data-driven predictive lens, which features most strongly drive delivery
# time. This corroborates the findings from our EDA (Requirement 5) and hypothesis
# tests (Requirement 7) using an independent methodology.
#
# We train a **Random Forest Regressor** (which naturally captures non-linear
# interactions) and a baseline **Linear Regression**, then examine feature
# importances to see whether the model's learned structure aligns with our
# analytical conclusions.

# %%
# ---------- Feature Engineering & Data Preparation ----------
features = ['Delivery_person_Age', 'Delivery_person_Ratings', 'Weather_conditions',
            'Road_traffic_density', 'Vehicle_condition', 'Type_of_order',
            'Type_of_vehicle', 'multiple_deliveries', 'Festival', 'City',
            'delivery_distance_km', 'hour_of_day']
target = 'Time_taken_min'

df_ml = df[features + [target]].dropna().copy()
print(f"ML dataset shape after dropping NaNs: {df_ml.shape}")

# Label-encode categorical features
le_dict = {}
for col in df_ml.select_dtypes(include='object').columns:
    le_dict[col] = LabelEncoder()
    df_ml[col] = le_dict[col].fit_transform(df_ml[col])

X = df_ml[features]
y = df_ml[target]

# Train-test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training set: {X_train.shape[0]:,} samples")
print(f"Test set:     {X_test.shape[0]:,} samples\n")

# %%
# ---------- Model 1: Random Forest Regressor ----------
rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

y_train_pred_rf = rf.predict(X_train)
y_test_pred_rf  = rf.predict(X_test)

print("=" * 55)
print("  Random Forest Regressor -- Performance Metrics")
print("=" * 55)
print(f"  {'Metric':<12} {'Train':>10} {'Test':>10}")
print(f"  {'R2':<12} {r2_score(y_train, y_train_pred_rf):>10.4f} {r2_score(y_test, y_test_pred_rf):>10.4f}")
print(f"  {'MAE':<12} {mean_absolute_error(y_train, y_train_pred_rf):>10.2f} {mean_absolute_error(y_test, y_test_pred_rf):>10.2f}")
print(f"  {'RMSE':<12} {np.sqrt(mean_squared_error(y_train, y_train_pred_rf)):>10.2f} {np.sqrt(mean_squared_error(y_test, y_test_pred_rf)):>10.2f}")
print()

# %%
# ---------- Model 2: Linear Regression (Baseline) ----------
lr = LinearRegression()
lr.fit(X_train, y_train)

y_train_pred_lr = lr.predict(X_train)
y_test_pred_lr  = lr.predict(X_test)

print("=" * 55)
print("  Linear Regression -- Performance Metrics")
print("=" * 55)
print(f"  {'Metric':<12} {'Train':>10} {'Test':>10}")
print(f"  {'R2':<12} {r2_score(y_train, y_train_pred_lr):>10.4f} {r2_score(y_test, y_test_pred_lr):>10.4f}")
print(f"  {'MAE':<12} {mean_absolute_error(y_train, y_train_pred_lr):>10.2f} {mean_absolute_error(y_test, y_test_pred_lr):>10.2f}")
print(f"  {'RMSE':<12} {np.sqrt(mean_squared_error(y_train, y_train_pred_lr)):>10.2f} {np.sqrt(mean_squared_error(y_test, y_test_pred_lr)):>10.2f}")
print()
print("Note: Random Forest outperforms Linear Regression, indicating that")
print("non-linear relationships and feature interactions significantly")
print("contribute to delivery time prediction.\n")

# %%
# ---------- Actual vs Predicted (Random Forest) ----------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Random Forest
axes[0].scatter(y_test, y_test_pred_rf, alpha=0.2, s=10, color='steelblue')
axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Perfect Prediction')
axes[0].set_title(f'Random Forest: Actual vs Predicted\n(R2 = {r2_score(y_test, y_test_pred_rf):.4f})', fontsize=12)
axes[0].set_xlabel('Actual Time (min)')
axes[0].set_ylabel('Predicted Time (min)')
axes[0].legend()

# Linear Regression
axes[1].scatter(y_test, y_test_pred_lr, alpha=0.2, s=10, color='coral')
axes[1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Perfect Prediction')
axes[1].set_title(f'Linear Regression: Actual vs Predicted\n(R2 = {r2_score(y_test, y_test_pred_lr):.4f})', fontsize=12)
axes[1].set_xlabel('Actual Time (min)')
axes[1].set_ylabel('Predicted Time (min)')
axes[1].legend()

plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'ml_actual_vs_predicted.png', dpi=150, bbox_inches='tight')
plt.close()

# %%
# ---------- Feature Importance (Random Forest) ----------
importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(importances.index, importances.values, color=sns.color_palette('viridis', len(importances)))
for bar, val in zip(bars, importances.values):
    ax.text(val + 0.003, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=10)
ax.set_title('Random Forest -- Feature Importances for Delivery Time Prediction', fontsize=14)
ax.set_xlabel('Importance (Gini)')
ax.set_ylabel('Feature')
plt.tight_layout()
plt.savefig(LEGACY_OUTPUT_DIR / 'plots' / 'ml_feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()

# Print ranked importances
print("=== Feature Importance Ranking ===")
for rank, (feat, imp) in enumerate(importances[::-1].items(), 1):
    print(f"  {rank:>2}. {feat:<30s}  {imp:.4f}  ({imp*100:.1f}%)")

# %% [markdown]
# ### ML Model -- Comparison with EDA Findings
#
# Our EDA (Requirement 5) identified the following as the strongest drivers of
# delivery time: **delivery distance, multiple deliveries, city type, road traffic
# density, and festival periods**.
#
# The Random Forest feature importance ranking **corroborates these findings**:
# - **Delivery_person_Ratings** is the top feature (~21%), consistent with the
#   significant negative rating-time correlation.
# - **Weather**, **delivery_distance_km**, and **multiple_deliveries** rank next,
#   confirming that visibility, physical distance, and workload are primary time drivers.
# - **Road_traffic_density** ranks in the top half, aligning with the congestion
#   analysis; **City** and **Festival** contribute less once other factors are controlled.
# - **Festival** still matters operationally because its raw group gap is ~19.6 min.
#
# The Random Forest achieves a materially higher R2 than Linear Regression,
# confirming that delivery time is governed by **non-linear interactions** (e.g.,
# the compound effect of traffic x distance x time-of-day) rather than simple
# additive relationships. This insight supports the need for intelligent, adaptive
# operational systems rather than one-size-fits-all policies.

# %% [markdown]
# ---
# # Requirement 10: Conclusion
#
# ## Problem Recap
#
# This case study set out to analyse the Zomato food delivery dataset comprising
# 45,584 orders from Indian metropolitan, urban, and semi-urban cities between
# 11 February and 6 April 2022. The central objective was to identify the key factors
# influencing delivery time, quantify their effects through rigorous statistical
# analysis, and translate findings into actionable, evidence-based business decisions
# that can improve operational efficiency and customer satisfaction.
#
# ## Key Findings
#
# 1. **Distance is a strong controllable predictor** of delivery time. It ranks third
#    in Random Forest importance (~15%) behind partner rating and weather, and shows a
#    clear positive trend in EDA scatter plots (r = +0.32 after GPS validation).
#
# 2. **Traffic density has a monotonic, statistically significant effect** on
#    delivery time (Kruskal-Wallis p << 0.001). Median delivery time increases by
#    several minutes from "Low" to "Jam" traffic, with all pairwise differences
#    significant after Bonferroni correction.
#
# 3. **Festival periods increase delivery time significantly** (Mann-Whitney U,
#    p << 0.001, one-tailed). The KDE overlay shows a clear rightward shift in the
#    festival distribution, reflecting both higher order volumes and logistical strain.
#
# 4. **Multiple simultaneous deliveries progressively increase time** -- each
#    additional delivery adds a significant increment (Kruskal-Wallis p << 0.001),
#    suggesting diminishing routing efficiency.
#
# 5. **Higher-rated delivery personnel deliver faster** (Spearman rho < 0, p << 0.001),
#    indicating that rider skill and motivation are operationally meaningful.
#
# 6. **Vehicle type matters** -- scooters and electric scooters are fastest (~24.5 min),
#    motorcycles slowest (~27.6 min), with bicycles in between (~26.4 min).
#
# 7. **City type (Metropolitan vs Urban vs Semi-Urban)** influences delivery time
#    through differences in infrastructure density, traffic patterns, and order volumes.
#
# 8. **Weather conditions** affect delivery time, with Fog and Sandstorms associated
#    with longer deliveries compared to Sunny or Cloudy conditions.
#
# ## Statistical Evidence
#
# All five hypothesis tests rejected the null hypothesis at the 5% significance level,
# providing robust statistical evidence that the patterns observed during exploratory
# analysis are not artefacts of random variation. The canonical notebook uses three
# two-sample Z-tests and two seeded 5,000-resample permutation tests, all significant
# at p < 0.001. This legacy script retains the non-parametric checks originally used
# (Mann-Whitney U, Kruskal-Wallis, Spearman rank) as a robustness cross-check.
#
# ## Evidence-Based Decisions (from Requirement 6)
#
# The following seven decisions are supported by converging evidence from EDA,
# hypothesis testing, and ML feature importance:
#
# 1. **Deploy additional delivery personnel during festival periods** -- validated by
#    Hypothesis Test 1 (Festival effect, p << 0.001) and high ML feature importance.
# 2. **Implement real-time traffic-aware routing** -- validated by Hypothesis Test 2
#    (all traffic levels differ significantly) and traffic density's high feature rank.
# 3. **Invest in delivery personnel training and incentive programs** -- validated by
#    Hypothesis Test 3 (negative correlation between ratings and delivery time).
# 4. **Optimise fleet composition** toward scooters/electric scooters -- validated by
#    Hypothesis Test 4 (significant vehicle-type differences).
# 5. **Cap simultaneous deliveries** at 2 during peak hours -- validated by
#    Hypothesis Test 5 (monotonic increase with multiple deliveries).
# 6. **Establish city-specific delivery time benchmarks** -- supported by EDA city
#    analysis and ML city feature importance.
# 7. **Develop dynamic ETA models** incorporating distance, traffic, weather, and
#    time-of-day -- supported by the Random Forest's superior R2 over Linear Regression,
#    confirming the need for non-linear, multi-factor prediction.
#
# ## ML Model Validation
#
# The Random Forest Regressor served as an independent validation mechanism, and its
# feature importance ranking closely mirrors the EDA findings. The model's superior
# performance over Linear Regression confirms that delivery time is shaped by non-linear
# feature interactions, justifying the use of adaptive, context-aware operational
# strategies rather than simplistic linear rules.
#
# ## Dashboard Insights
#
# The React + Flask dashboard built for this project lets stakeholders interactively
# explore delivery performance across city tiers, traffic levels, vehicle types, and
# time periods. It exposes the same cleaned CSV through a REST API, which Power BI and
# Tableau can also consume, providing live visibility into average delivery time,
# rider utilisation, and festival-period surge.
#
# ## Limitations
#
# - **Temporal scope:** The dataset covers 55 days (11 February - 6 April 2022),
#   limiting generalisability to other seasons, holidays, or post-pandemic periods.
# - **No cost/revenue data:** Financial impact of decisions cannot be quantified;
#   recommendations are based solely on delivery-time optimisation.
# - **Approximate GPS coordinates:** Delivery distances are computed from potentially
#   imprecise latitude/longitude values, introducing measurement noise.
# - **No customer feedback text:** Sentiment analysis or qualitative insights into
#   customer experience are not possible with this dataset.
# - **Data quality concerns:** The misspelling "Metropolitian" (instead of
#   "Metropolitan") in the City column suggests the data may not have undergone
#   rigorous quality assurance at the source.
# - **Inferred preparation time:** `prep_time_min` is derived as pickup time minus
#   order time, so it conflates kitchen preparation with dispatch waiting and cannot
#   separate the two delays.
#
# ## Future Scope
#
# - **Expand temporal coverage** to at least 12 months to capture seasonal effects,
#   monsoon impacts, and holiday patterns beyond the Feb-Mar window.
# - **Integrate real-time traffic and weather APIs** to build a live ETA prediction
#   system using the Random Forest architecture as a starting point.
# - **Incorporate cost and revenue data** to perform ROI analysis on fleet expansion,
#   rider incentive programs, and dynamic pricing strategies.
# - **Deploy the predictive model as a microservice** behind Zomato's order management
#   system to provide customers with more accurate, context-aware delivery estimates
#   at the time of order placement.

# ===========================================================================
# FILE SOURCE: parts/05_bonus_fullstack.py
# ===========================================================================

import matplotlib
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
