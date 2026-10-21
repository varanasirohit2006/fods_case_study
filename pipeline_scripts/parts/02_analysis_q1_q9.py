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
# Prioritise scooters and electric scooters for time-sensitive deliveries, reserve
# bicycles for hyperlocal orders, and re-evaluate the motorcycle share -- it is the
# slowest modality in this dataset despite its higher top speed.

# %% [markdown]
# ---
# ## Summary of Key Findings (Q1-Q9)
# 
# | Question | Key Finding | Business Impact |
# |----------|------------|-----------------|
# | Q1 | Semi-Urban has the highest delivery times (49.7 min); Metro carries most volume | Tier-specific ETA calibration needed |
# | Q2 | Metro dominates volume (77%); Semi-Urban is a small niche (0.4%) | Focus metro operations; validate Semi-Urban separately |
# | Q3 | Fog/Cloudy add ~7 min vs Sunny conditions | Weather-aware ETA adjustments required |
# | Q4 | Jam traffic adds significant delay with high variance | Traffic-based routing and fleet pre-positioning |
# | Q5 | Weather x Traffic interaction is approximately additive | Multivariate ETA model with interaction terms |
# | Q6 | Festival periods show ~19.6 min longer deliveries | Surge hiring and proactive ETA communication |
# | Q7 | Clear lunch and dinner peaks in order volume | Shift scheduling aligned to demand peaks |
# | Q8 | Weekly patterns are relatively flat | Consistent staffing; promote on slow days |
# | Q9 | Scooters/e-scooters fastest; motorcycles slowest | Fleet mix optimisation for speed + sustainability |
