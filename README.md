# Zomato FoDS Case Study — Dashboard & Full-Stack Guide (Requirement 9 + Bonus)

> **What this file is:** the exact, click-by-click instructions to complete **Rubric 9 (Power BI / Tableau visualization)** and the **Bonus (backend + full-stack integration)** for this case study.
> The notebook `Zomato_FoDS_Case_Study.ipynb` already contains the dashboard **design** (cell 100) and the backend **documentation** (cells 102–103). What is still missing is the **actual dashboard artifact** (`.pbix` / `.twbx` / published link) and the **evidence screenshots** of Power BI/Tableau consuming the live API.
> Follow this top to bottom. Do not skip Part D — that is exactly what earns the marks.

---

## 0. Repository map (what is what)

| Path | Purpose |
|---|---|
| `Zomato_FoDS_Case_Study.ipynb` | **Canonical deliverable** — all 10 requirements executed with outputs. Do not modify if already submitted. |
| `Zomato Dataset.csv` | Raw data (45,584 rows × 20 cols). |
| `cleaned_zomato_data.csv` | Cleaned data (45,584 rows × 26 cols) — the file Power BI/Tableau read for the static dashboard. |
| `plots/` | All notebook charts (EDA, Q1–Q15, hypothesis tests, ML). |
| `app.py` | Flask REST API backend (13 endpoints, CORS enabled, serves CSV + ML predictions). |
| `zomato_prep.py`, `zomato_model.py` | Shared cleaning + model helpers used by `app.py`. |
| `rf_delivery_model.joblib` | Trained serving model for `/api/predict` (holdout R² = 0.8158, MAE = 3.18 min). |
| `frontend/` | React + Vite dashboard (calls the Flask API, falls back to cached mock data). |
| `pipeline_scripts/` | Legacy build scripts. Not needed for grading. |

**Quick-start commands (PowerShell, project root):**

```powershell
cd "C:\Users\varan\OneDrive\Desktop\5thsem\fods_main\fods_zomato"

# 1. Backend (needed for the bonus live feed; optional for the static dashboard)
pip install -r requirements.txt
python app.py        # → http://127.0.0.1:5000

# 2. React frontend (optional bonus demo)
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

---

## 1. Rubric audit (current status of the notebook)

| # | Rubric | Status | Where |
|---|---|---|---|
| 1 | Real data set | Done | Cells 2–4 (45,584 × 20 Zomato CSV). |
| 2 | Preprocessing & EDA | Done | Cells 5–6 (imputation counts, type casting, Haversine, prep time, temporal features) + EDA 1–11 (cells 7–40). |
| 3 | Learnings from data | Done | Cell 41 — 11 takeaways tied to EDAs. |
| 4 | 15+ analytical questions | Done | Cell 42 + Q1–Q15 (cells 43–86). |
| 5 | Per-question analysis + justification + visualization | Done | Each Q: Domain Reason → Graph Justification → Expected Revelation → Code+Chart → Results/Interpretation/Decision. |
| 6 | Decisions | Done | Cell 88 — 7 decisions with evidence mapping. |
| 7 | Hypothesis testing proof | Done | Cells 89–95 — 5 tests (3 Z-tests + 2 permutation tests) + Type I/II error discussion. |
| 8 | ML model + justification | Done (framed as *supporting validation only*, per "no ML projects" rule) | Cells 96–99 — LR vs RF, R² 0.4954 vs 0.8271. |
| 9 | **Power BI / Tableau visualization** | **NOT DONE — only a spec exists** | Cell 100 has the 5-page layout + DAX. No `.pbix`/`.twbx`, no screenshots, no dashboard anywhere. |
| 10 | Conclusion | Done | Cell 101. |
| Bonus | Backend + full-stack integration | Half done | `app.py` + `frontend/` exist and endpoints verified (cell 103). Missing: proof that Power BI/Tableau actually consumed the API. |

**Known minor gaps (viva ammunition, not failures):**
- Notebook cells 90–92 (Tests 1–3) print results but show **no chart inline**; matching PNGs (`plots/ht1_festival_kde.png`, `ht2_traffic_boxplot.png`, `ht3_ratings_correlation.png`, `ht5_multiple_deliveries_bar.png`) exist but were produced by the legacy pipeline. If the evaluator wants a visual per test, attach those PNGs in your report.
- No root README existed before this file — run instructions are now here.

---

## 2. PART A — Power BI static dashboard (this is Rubric 9)

**Why Power BI first:** free, the DAX is already written in the notebook (cell 100), and it supports the live-API bonus that Tableau cannot do natively.

### Step A1 — Install Power BI Desktop
1. Open **Microsoft Store** → search **"Power BI Desktop"** → Install (free).
2. Open it. Skip any sign-in prompt for now (not needed for the static dashboard).

### Step A2 — Import the cleaned CSV
1. On the Home ribbon: **Get data → Text/CSV**.
2. Browse to `C:\Users\varan\OneDrive\Desktop\5thsem\fods_main\fods_zomato\cleaned_zomato_data.csv` → **Open**.
3. In the preview window click **Transform Data** (do NOT click Load yet).

### Step A3 — Fix column types (Power Query Editor)
Click the small type icon left of each column name and set:

| Column(s) | Type |
|---|---|
| `Order_Date` | Date |
| `Delivery_person_Age`, `Vehicle_condition`, `multiple_deliveries`, `hour_of_day`, `day_of_week_num`, `month`, `Time_taken_min`, `prep_time_min` | Whole Number |
| `Delivery_person_Ratings`, `delivery_distance_km`, all 4 latitude/longitude columns | Decimal Number |
| `ID`, `Delivery_person_ID`, `Weather_conditions`, `Road_traffic_density`, `Type_of_order`, `Type_of_vehicle`, `Festival`, `City`, `day_of_week`, times | Text (leave as-is) |

Notes:
- `delivery_distance_km` has **431 blanks** (invalid GPS masked by the notebook). Leave them — scatter plots simply skip those rows.
- The city value is spelled **"Metropolitian"** in the source data (typo). Keep it; just be consistent in filters.

4. Click **Home → Close & Apply**.

### Step A4 — Create the measures (copy-paste, one at a time)
Go to **Data view** (left sidebar, the table icon). Select table `cleaned_zomato_data` → ribbon **Table tools / Modeling → New measure** → paste → Enter. Repeat for each:

```dax
Average Delivery Duration = AVERAGE('cleaned_zomato_data'[Time_taken_min])

Total Orders = COUNTROWS('cleaned_zomato_data')

Active Fleet = DISTINCTCOUNT('cleaned_zomato_data'[Delivery_person_ID])

Fleet Avg Rating = AVERAGE('cleaned_zomato_data'[Delivery_person_Ratings])

SLA Breach Rate =
DIVIDE(
    CALCULATE(COUNTROWS('cleaned_zomato_data'), 'cleaned_zomato_data'[Time_taken_min] > 35),
    COUNTROWS('cleaned_zomato_data'),
    0
)

Batching Penalty Delta =
CALCULATE(AVERAGE('cleaned_zomato_data'[Time_taken_min]), 'cleaned_zomato_data'[multiple_deliveries] >= 2)
- CALCULATE(AVERAGE('cleaned_zomato_data'[Time_taken_min]), 'cleaned_zomato_data'[multiple_deliveries] < 2)
```

Select `SLA Breach Rate` → Format ribbon → **Percentage** (0 decimals).

### Step A5 — Build Page 1: Executive Operations Overview
Rename the page (right-click the tab at the bottom) to **"1. Executive Overview"**.

1. **KPI cards** — Visualizations pane → **Card** visual. Make 4 cards:
   - Card 1: drag `Total Orders`
   - Card 2: drag `Average Delivery Duration`
   - Card 3: drag `Active Fleet`
   - Card 4: drag `Fleet Avg Rating`
2. **Daily volume trend** — Visualizations → **Line chart**. X-axis: `Order_Date`; Y-axis: `Total Orders`.
3. **City breakdown** — Visualizations → **Donut chart**. Legend: `City`; Values: `Total Orders`.
4. **Traffic tier bar** — Visualizations → **Clustered bar chart**. Y-axis: `Road_traffic_density`; X-axis: `Total Orders`.
5. **Slicers** (this page, and copy to other pages later):
   - **Slicer** visual → Field: `Order_Date` → format as "Between" (date range).
   - **Slicer** visual → Field: `City`.
   - **Slicer** visual → Field: `Festival`.

### Step A6 — Build Page 2: Bottleneck & Environmental Analysis
New page (bottom **+**) → rename **"2. Bottlenecks"**.

1. **Weather impact bar with CI** — Clustered bar chart. Y-axis: `Weather_conditions`; X-axis: `Average Delivery Duration`.
   - Error bars: select the visual → Format pane → **Error bars → On** → Upper bound: `Average Delivery Duration` *change aggregation to a standard deviation* — simplest: right-click the field in the well → **Don't summarize**, or add a second measure `Time SD = STDEV.P('cleaned_zomato_data'[Time_taken_min])` and use that. *(If error bars get fiddly, a plain average bar is acceptable — the notebook already shows the 95% CI version in `plots/q3_weather_delivery_time.png`.)*
2. **Traffic comparison** — Clustered column chart. X-axis: `Road_traffic_density` ordered Low→Medium→High→Jam (right-click axis → Sort axis → by `Average Delivery Duration` ascending is wrong; better: create a sort column). Simplest exact way:
   - Data view → New column:
     ```dax
     Traffic Order = SWITCH('cleaned_zomato_data'[Road_traffic_density],
         "Low", 1, "Medium", 2, "High", 3, "Jam", 4, 5)
     ```
   - Select the `Road_traffic_density` column → **Column tools → Sort by column → `Traffic Order`**.
3. **Weather × Traffic heatmap** — Visualizations → **Matrix**.
   - Rows: `Weather_conditions`; Columns: `Road_traffic_density`; Values: `Average Delivery Duration`.
   - Format pane → **Cell elements → Background color → On** → set a color scale (white→red). This reproduces notebook Q5 exactly (worst: Fog+Jam = 36.8 min).
4. Copy the 3 slicers from Page 1: click a slicer → **Ctrl+C**, go to Page 2 → **Ctrl+V** (do this for all later pages).

### Step A7 — Build Page 3: Fleet & Partner Performance
New page → rename **"3. Fleet & Partners"**.

1. **Rating tier vs duration** — Clustered column chart. X-axis: `Delivery_person_Ratings` (as a hierarchy? simpler: create a column):
   ```dax
   Rating Tier =
   SWITCH(TRUE(),
       'cleaned_zomato_data'[Delivery_person_Ratings] < 2, "1.0-2.0",
       'cleaned_zomato_data'[Delivery_person_Ratings] < 3, "2.0-3.0",
       'cleaned_zomato_data'[Delivery_person_Ratings] < 4, "3.0-4.0",
       'cleaned_zomato_data'[Delivery_person_Ratings] < 4.5, "4.0-4.5",
       "4.5-5.0")
   ```
   X-axis: `Rating Tier`; Y-axis: `Average Delivery Duration`.
2. **Vehicle category comparison** — Clustered bar chart. Y-axis: `Type_of_vehicle`; X-axis: `Average Delivery Duration`.
3. **Vehicle condition impact** — Clustered column chart. X-axis: `Vehicle_condition`; Y-axis: `Average Delivery Duration`.
4. Add a slicer: `Type_of_vehicle`.

### Step A8 — Build Page 4: Logistics & Order Batching Monitor
New page → rename **"4. Batching & Demand"**.

1. **Batching penalty** — Clustered column chart. X-axis: `multiple_deliveries`; Y-axis: `Average Delivery Duration`. Add data labels (Format → Data labels → On).
2. **Hourly demand vs duration (dual axis)** — Visualizations → **Line and clustered column chart**.
   - X-axis: `hour_of_day`
   - Column y-axis: `Total Orders`
   - Line y-axis: `Average Delivery Duration`
3. **Distance vs time scatter** — Visualizations → **Scatter chart**. X-axis: `delivery_distance_km` (set aggregation to **Don't summarize**); Y-axis: `Time_taken_min` (Don't summarize); Details: `City`.
   - Optional trend line: Analytics pane → **Trend line → On**.
4. **Drill-through**: on this page, Visualizations → **Drill through → Add drill-through fields here** → drag `City`. Now right-clicking a city on Page 1 lets you "Drill through → 4. Batching & Demand".

### Step A9 — Build Page 5: Strategic Decisions & ROI Tracker
New page → rename **"5. Decisions"**.

1. **What-if parameter**: ribbon **Modeling → New parameter → Numeric range**. Name: `Batching Cap`; Minimum 1, Maximum 3, Increment 1; Add slicer → **Create**. You get a slider on the page.
2. **Scenario measure** — New measure:
   ```dax
   Avg Time At Batching Cap =
   VAR capVal = SELECTEDVALUE('Batching Cap'[Batching Cap])
   RETURN
       CALCULATE(
           AVERAGE('cleaned_zomato_data'[Time_taken_min]),
           'cleaned_zomato_data'[multiple_deliveries] <= capVal
       )
   ```
3. Add a **Card** with `Avg Time At Batching Cap` next to the slider. Moving the slider 1→2→3 shows the modelled average (~26.7 min at cap 1 → ~27.3 at cap 2 → ~27.4 at cap 3 — the 2+3 batches get included as the cap rises). State in the report this is a what-if model of the observed batch durations, not a causal forecast.
4. **Decisions table** — Visualizations → **Table**. Columns: paste content manually or build from the notebook cell 88 table (7 decisions, evidence, impact). A plain table with typed-in text is fine.
5. Optional: card with `Batching Penalty Delta` (≈ +16 min).

### Step A10 — Polish
- Insert → **Text box** on Page 1 with the case-study title and "Source: cleaned_zomato_data.csv | 45,584 orders".
- Add a **Card** or text box "Refreshed: " and a measure `Refreshed = NOW()` so the timestamp is visible in screenshots.
- Rename the report: **File → Options → Current file → Report settings** (optional).

### Step A11 — Export the evidence (this is what the grader sees)
1. **File → Save as** → save as `Zomato_Delivery_Dashboard.pbix` in the project root (or a new `dashboard/` folder).
2. **File → Export → Export to PDF** → save `Zomato_Delivery_Dashboard.pdf`.
3. Take **PNG screenshots of all 5 pages** (Win+Shift+S), saved as `dashboard_p1.png` … `dashboard_p5.png`.
4. (Optional, not required) Publish: **Home → Publish** needs a work/school Microsoft account. If you don't have one, the PDF + `.pbix` + screenshots are sufficient.

---

## 3. PART B — BONUS: feed the live backend into Power BI

Goal: prove that Power BI is not just reading a CSV but is connected to your **Flask REST API** — this is literally the bonus sentence in the assignment.

### Step B1 — Start the backend and verify it in a browser
1. Open PowerShell in the project root:
   ```powershell
   cd "C:\Users\varan\OneDrive\Desktop\5thsem\fods_main\fods_zomato"
   pip install flask flask-cors
   python app.py
   ```
   Expected output: `Starting Zomato Analytics API on http://127.0.0.1:5000` and `Dataset loaded: ...` plus `Model bundle ready`.
2. In a browser open `http://127.0.0.1:5000/` → you should see the red "Zomato Delivery Analytics API" page listing all endpoints.
3. Open `http://127.0.0.1:5000/api/kpis` → you should see JSON with `total_orders: 45584`.
**Leave this PowerShell window running.**

### Step B2 — Connect Power BI to the live API
In Power BI Desktop (same machine):

1. **Get data → Web** → URL: `http://127.0.0.1:5000/api/kpis` → OK.
2. Power Query opens showing a **single Record** → click **Into Table** (Home/Transform ribbon) → the record becomes one row → click the **expand icon (⇔)** in the column header → select all fields → OK → rename query to `KPI_Live`.
3. Repeat **Get data → Web** for each endpoint in the table below. What you do after import depends on the JSON shape:

| Query name | URL | What Power Query shows → what to click |
|---|---|---|
| `KPI_Live` | `/api/kpis` | Record → **Into Table** → expand |
| `City_Live` | `/api/delivery-time/by-city` | **List of records** → **To Table** → expand `Column1` |
| `Weather_Live` | `/api/delivery-time/by-weather` | same as above |
| `Traffic_Live` | `/api/delivery-time/by-traffic` | same as above |
| `Vehicle_Live` | `/api/delivery-time/by-vehicle` | same as above |
| `Hour_Live` | `/api/delivery-time/by-hour` | same as above (columns: hour, mean_time, order_count) |
| `Festival_Live` | `/api/delivery-time/by-festival` | same as above |
| `Decisions_Live` | `/api/decisions` | Record → Into Table → expand the `decisions` column (nested list of 7 records) |
| `Filtered_Live` | `/api/filtered-data?traffic=Jam` | Record → Into Table → expand `data` (up to 1,000 rows) |
| `Predict_Live` | `/api/predict?distance=8&weather=Fog&traffic=Jam&city=Metropolitian&vehicle=scooter&rating=4.6&hour=20` | Record → Into Table → expand → shows `predicted_delivery_time_min` |

Full base URL for every row above: `http://127.0.0.1:5000` + the path.

Allowed values if you edit the filter parameters: `city` = Metropolitian / Urban / Semi-Urban · `weather` = Sunny / Cloudy / Fog / Sandstorms / Stormy / Windy · `traffic` = Low / Medium / High / Jam · `festival` = Yes / No · `vehicle` = motorcycle / scooter / electric_scooter / bicycle · `order_type` = Snack / Meal / Drinks / Buffet.

4. **Close & Apply**.
5. Optional but strong: build a **"6. Live Ops Feed" page** with a card for `KPI_Live[avg_delivery_time]` and a bar chart from `City_Live` (X = city, Y = mean_time) — these values come from the API, not the CSV.

### Step B3 — Demonstrate the live feed (this is your bonus evidence)
1. With Power BI open on the Live page, press **Home → Refresh** (or Ctrl+Alt+F5). The values reload from Flask.
2. Screenshot three things side by side in one image (or a 2-panel screenshot):
   - Browser showing `http://127.0.0.1:5000/api/kpis` JSON,
   - PowerShell running `python app.py`,
   - Power BI Live page after refresh.
3. Bonus-of-bonus: edit `cleaned_zomato_data.csv` (e.g., add a row in Excel, or change one `Time_taken_min`), press **Refresh** in Power BI, and show the KPI card value change. Revert the file afterwards.
4. Note for the report: scheduled refresh on Power BI Service would require an on-premises data gateway because the API runs on localhost; manual refresh is the demo path.

### Step B4 — (Optional) React frontend demo for the "full stack" story
```powershell
cd "C:\Users\varan\OneDrive\Desktop\5thsem\fods_main\fods_zomato\frontend"
npm install
npm run dev
```
Open `http://localhost:5173`. The frontend calls the Flask API via a Vite proxy (`/api` → `127.0.0.1:5000`) and falls back to cached data if the API is off. Screenshot: React dashboard + Flask + Power BI = the full stack.

---

## 4. PART C — Tableau alternative (if you prefer Tableau, or want both)

Use **Tableau Public** (free). Note upfront: **Tableau cannot natively pull an arbitrary REST JSON URL** without a Web Data Connector — so do the live-backend part in Power BI and the static dashboard here (or export the API JSON files and import those).

1. Download **Tableau Public Desktop** → install → create a free account (needed to publish).
2. **Connect → To a File → Text file** → `cleaned_zomato_data.csv`.
3. Drag `Order_Date` to the Data Source page and confirm it parsed as Date; check `Time_taken_min` is a Number.
4. Build sheets (bottom tabs), then assemble them in a Dashboard:
   - **KPIs**: drag `Number of Records` or `Time_taken_min` (AVG) to **Text** to make a big-number sheet; use 4 separate sheets for 4 KPI cards.
   - **Weather bars**: Columns = `Weather_conditions`, Rows = `AVG(Time_taken_min)`.
   - **Traffic box plot**: Columns = `Road_traffic_density`, Rows = `Time_taken_min` → **Show Me → Box-and-whisker** (Tableau has this natively; Power BI does not).
   - **Weather × Traffic heatmap**: `Weather_conditions` on Rows, `Road_traffic_density` on Columns, `AVG(Time_taken_min)` on Color and Label → **Show Me → Highlight Table**.
   - **Hourly dual axis**: Columns = `hour_of_day`; Rows = `AVG(Time_taken_min)`; drag `Number of Records` next to it → right-click second pill → **Dual Axis**; set one to Bar, other to Line (synchronize axes off for the two measures).
   - **Batching**: Columns = `multiple_deliveries`, Rows = `AVG(Time_taken_min)`.
   - **Distance scatter**: Columns = `delivery_distance_km`, Rows = `Time_taken_min` (both unaggregated) → Marks = Circle; Analytics pane → Trend Line.
   - **Rating tiers**: create a calculated field (IF/ELSEIF on `Delivery_person_Ratings` = same bins as the notebook), or use rating bins.
5. **Dashboard**: drag the sheets in; add **filters** for `Order_Date` (range), `City`, `Festival`, and set each filter to **Apply to all worksheets using this data source**.
6. **Publish**: Server → **Tableau Public → Save to Tableau Public** → copy the shareable link.
   - Offline copy: **File → Export Packaged Workbook (.twbx)** → submit this file.
7. Evidence: screenshots of every dashboard + the Tableau Public link.

---

## 5. PART D — Submission checklist (exact evidence list)

For **Rubric 9**:
- [ ] `Zomato_Delivery_Dashboard.pbix` (or `.twbx` / Tableau Public link)
- [ ] `Zomato_Delivery_Dashboard.pdf` export
- [ ] 5 page screenshots `dashboard_p1.png` … `dashboard_p5.png`
- [ ] One-page **traceability table** (copy from §7 below): dashboard visual → notebook Q#/test → decision. This shows the dashboard *is* the analysis, not decoration.

For the **Bonus**:
- [ ] PowerShell window showing `python app.py` running
- [ ] Browser screenshot of `http://127.0.0.1:5000/` (endpoint list) and `/api/kpis` (JSON)
- [ ] Power BI "Live Ops Feed" page screenshot taken **after** a refresh
- [ ] One paragraph in the report: architecture (CSV → Flask → Power BI/Tableau/React), manual refresh note, and the localhost/gateway caveat
- [ ] (Optional) React frontend screenshot at `localhost:5173`

---

## 6. PART E — Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `DataSource.Error: Web.Contents failed to get contents` on refresh | Flask not running | Start `python app.py` first; verify in browser. If the API is down, Power BI uses the last loaded data — only the Web queries error. |
| Port 5000 busy | Another process uses it | Run `$env:ZOMATO_API_PORT="5050"; python app.py` and use `http://127.0.0.1:5050/...` in Power BI. |
| Windows Firewall prompt on first `python app.py` | Normal | Click **Allow** (private networks). |
| Bar chart shows a huge number (e.g. millions) | Power BI auto-summed `Time_taken_min` | Right-click the field in the visual's well → **Average** (or use the `Average Delivery Duration` measure). |
| Box plot not available in Power BI | Not a native visual | AppSource → "Box and Whisker chart" custom visual, or use median/p25/p75 measures, or use Tableau for that page. |
| Semi-Urban bars look odd | Only 164 rows vs 35,287 metro | Add `Total Orders` to tooltip so the sample size is visible; it's a real finding (Q1), not an error. |
| Scatter has gaps | 431 blank `delivery_distance_km` (invalid GPS masked) | Expected; documented in notebook §10.4. |
| City filter shows "Metropolitian" | Source-data typo kept intentionally | Fine — notebook and API use the same spelling. |
| `npm run dev` fails | Node.js missing | Install Node LTS from nodejs.org, then `npm install` again. |
| Tableau can't fetch the JSON URL | No native REST connector | Use the CSV/JSON-file route in Tableau; keep live REST in Power BI. |

---

## 7. Appendix — Traceability table (dashboard visual → notebook proof)

| Dashboard page / visual | Notebook evidence |
|---|---|
| P1 KPI cards (26.3 min, 45,584 orders, 1,320 fleet, 4.64 rating) | EDA 1–6, cell 41 |
| P1 Donut by `City` | Q1, Q2 |
| P1 Traffic bar | EDA 5, Q4 |
| P2 Weather bars | Q3 |
| P2 Traffic comparison | Q4, Test 3 (z = +96.98) |
| P2 Weather × Traffic matrix/heatmap | Q5 (Fog+Jam = 36.8 min) |
| P3 Rating tier chart | Q12 (r = −0.333) |
| P3 Vehicle comparison | Q9, Test 4 (permutation p < 0.0002) |
| P3 Vehicle condition chart | Q10 (+5.72 min at condition 0) |
| P4 Batching chart | Q14, Test 5 (+16.12 min) |
| P4 Hourly dual-axis | Q7 (7–9 PM peak) |
| P4 Distance scatter | Q15 (r = 0.3216) |
| P5 What-if `Batching Cap` | Decision 5, permutation test |
| P5 Decisions table | Cell 88 (7 decisions) |
| P6 (bonus) Live Ops Feed | Cells 102–103, `app.py` |

*File generated as the companion guide for `Zomato_FoDS_Case_Study.ipynb`. The notebook itself was not modified.*
