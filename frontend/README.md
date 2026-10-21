# 🍽️ Zomato Operations & Delivery Analytics Web Application

A full-stack interactive web application built with **React, TypeScript, Vite, Tailwind CSS, and Recharts**, connected to the Python Flask REST API (`app.py`) for the **Foundation of Data Science (FoDS - 23CSE351)** Case Study.

---

## 🚀 Quick Start Guide

### 1. Launch the Backend API (Terminal 1)

```bash
# In the root project directory:
python app.py
```

*Backend runs on `http://127.0.0.1:5000` with 13 REST API endpoints and CORS enabled.*

---

### 2. Launch the React Web Application (Terminal 2)

```bash
# Move into the frontend directory:
cd frontend

# Start the Vite development server:
npm run dev
```

*Open your browser at `http://localhost:3000`.*

---

## 🌟 Key Application Features

| Module                          | Features & Scientific Methodologies                                                                                                                                                                                                                              | Connected Flask API                                                                                                              |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **📊 Overview & KPIs**    | Live platform counters, 45,584 order metrics, city distribution donut chart, traffic escalation bar chart, realistic Indian delivery photography.                                                                                                                | `GET /api/kpisGET /api/delivery-time/by-city``GET /api/delivery-time/by-traffic`                                               |
| **⏱️ Delivery Drivers** | Dual-axis hourly volume vs SLA latency curve (Q7), atmospheric weather profiles (Q3), holiday surge shock analysis (Q6 & Test 2), multi-factor extreme combinations table (API analysis).                                                                        | `GET /api/delivery-time/by-hourGET /api/delivery-time/by-weather``GET /api/delivery-time/by-festivalGET /api/top-combinations` |
| **🛵 Fleet Intelligence** | Vehicle modality agility comparison (Q9), permutation tested 5,000 resamples for scooters vs motorcycles (Test 4), order batching penalty breakdown (Test 5), rider age & rating demographics (Q11, Q12).                                                        | `GET /api/delivery-time/by-vehicleGET /api/partner-analysis`                                                                   |
| **🤖 AI ETA Predictor**   | Interactive parameter simulator (sliders for distance, weather, traffic congestion, batching, vehicle type, and dispatch hour). Connects to the pre-trained Random Forest serving model (holdout $R^2 = 0.8158$, RMSE 4.03 min) with an RMSE-based error band. | `GET /api/predictGET /api/model-info`                                                                                          |
| **🔍 Dataset Explorer**   | Multi-attribute transactional table viewer with search filtering across 45,584 orders, live subset statistics, and pagination.                                                                                                                                   | `GET /api/filtered-data`                                                                                                       |
| **💡 Strategic Playbook** | 7 Executive evidence-based logistical interventions (Requirement 6) with statistical backing, operational impact metrics, and realistic visual cards.                                                                                                            | `GET /api/decisions`                                                                                                           |

---

## 🛡️ Zero-Failure Architecture

The frontend features an intelligent fallback layer:

- If the Flask backend is running on `http://127.0.0.1:5000`, the app **dynamically streams live data** and displays the **🟢 API Live** indicator.
- If the backend is paused or starting up, the app automatically serves from an authentic, verified pre-computed cache of the **45,584 records**, ensuring the user interface always loads with zero broken charts or missing states.
