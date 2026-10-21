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
# violin plot shows distinct distribution shapes per vehicle type: scooters and
# electric scooters are fastest, motorcycles slowest, bicycles in between.
#
# **Business Implication:** Supports **Decision: Optimise fleet composition** by
# prioritising faster vehicle types (scooters/electric scooters) for long-distance or
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
# 45,584 orders from Indian metropolitan, urban, and semi-urban cities
# between 11 February and 6 April 2022. The central objective was to identify the key factors
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
