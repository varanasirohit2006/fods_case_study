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
os.makedirs('plots', exist_ok=True)

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
