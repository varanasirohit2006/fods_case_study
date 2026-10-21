import React, { useState, useEffect } from 'react'
import { PredictionRequest, PredictionResponse } from '../types'
import { predictDeliveryTime } from '../api'
import { REAL_IMAGES } from '../data/mockData'
import {
  Sparkles,
  Sliders,
  Clock,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Info,
  MapPin,
  Flame,
} from 'lucide-react'

export const AIPredictor: React.FC = () => {
  const [params, setParams] = useState<PredictionRequest>({
    distance: 6.5,
    weather: 'Sunny',
    traffic: 'Medium',
    city: 'Metropolitian',
    vehicle: 'scooter',
    vehicle_condition: 2,
    multiple_deliveries: 0,
    festival: 'No',
    age: 30,
    rating: 4.8,
    hour: 19,
  })

  const [prediction, setPrediction] = useState<number | null>(25.8)
  const [loading, setLoading] = useState<boolean>(false)
  const [isLiveApi, setIsLiveApi] = useState<boolean>(false)
  const [modelMetrics, setModelMetrics] = useState<{ r2: number; mae: number; rmse: number } | null>(null)

  // Dataset group means shown as contextual benchmarks (not additive model terms).
  const TRAFFIC_BENCH: Record<string, number> = { Low: 21.46, Medium: 26.7, High: 27.24, Jam: 31.18 }
  const WEATHER_BENCH: Record<string, number> = { Sunny: 21.86, Cloudy: 28.92, Fog: 28.74, Windy: 26.12, Sandstorms: 25.88, Stormy: 25.87 }
  const BATCH_BENCH: Record<number, number> = { 0: 22.88, 1: 26.72, 2: 40.45, 3: 47.82 }

  // Recalculate on parameter changes
  useEffect(() => {
    let active = true
    const runPrediction = async () => {
      setLoading(true)
      const res = await predictDeliveryTime(params)
      if (active) {
        setPrediction(res.data.predicted_delivery_time_min)
        setModelMetrics(res.data.model_metrics || null)
        setIsLiveApi(res.isLive)
        setLoading(false)
      }
    }

    const timer = setTimeout(runPrediction, 200)
    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [params])

  // SLA status classification
  const getSlaStatus = (time: number) => {
    if (time <= 30) {
      return {
        label: 'SLA Guaranteed (Sub-30m)',
        color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
        icon: ShieldCheck,
      }
    }
    if (time <= 38) {
      return {
        label: 'Moderate Traffic Buffer (30-38m)',
        color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
        icon: Clock,
      }
    }
    return {
      label: 'Severe SLA Risk Buffer (>38m)',
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      icon: AlertTriangle,
    }
  }

  const sla = prediction ? getSlaStatus(prediction) : null
  const SlaIcon = sla?.icon

  return (
    <div className="space-y-8">
      
      {/* 1. Header Banner */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <Sparkles className="w-4 h-4" />
              <span>Machine Learning Validation • Requirement 8 & API /api/predict</span>
            </div>
            <h2 className="text-xl font-extrabold text-white">Live AI Delivery Time Simulator</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Interact with the Random Forest predictive model (R² = {modelMetrics?.r2 ?? 0.8158}) trained on 11 operational variables. Adjust environmental, route, and partner parameters to evaluate simulated transit ETAs.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${
              isLiveApi 
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
            }`}>
              {isLiveApi ? '🟢 Flask Model Connected' : '⚡ Local ML Inference'}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Interactive Control Matrix + Live Result Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Sliders & Controls */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-rose-400" />
              Operational Parameters
            </h3>
            <button
              onClick={() =>
                setParams({
                  distance: 5.0,
                  weather: 'Sunny',
                  traffic: 'Medium',
                  city: 'Metropolitian',
                  vehicle: 'scooter',
                  vehicle_condition: 2,
                  multiple_deliveries: 0,
                  festival: 'No',
                  age: 30,
                  rating: 4.8,
                  hour: 14,
                })
              }
              className="text-xs text-slate-400 hover:text-rose-400 transition cursor-pointer flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" /> Reset Defaults
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            
            {/* Slider 1: Route Distance */}
            <div className="space-y-2 sm:col-span-2">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-slate-300">Route Distance (Haversine)</span>
                <span className="font-mono font-bold text-rose-400">{params.distance} km</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="20"
                step="0.5"
                value={params.distance}
                onChange={(e) => setParams({ ...params, distance: parseFloat(e.target.value) })}
                className="w-full accent-rose-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>0.5 km (Hyperlocal)</span>
                <span>9.7 km (Fleet Avg)</span>
                <span>20 km (Long Range)</span>
              </div>
            </div>

            {/* Select 1: Weather Conditions */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Weather Condition</label>
              <select
                value={params.weather}
                onChange={(e) => setParams({ ...params, weather: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500"
              >
                <option value="Sunny">Sunny (Optimal: 21.9m)</option>
                <option value="Cloudy">Cloudy (28.9m)</option>
                <option value="Fog">Fog (28.7m)</option>
                <option value="Stormy">Stormy (25.9m)</option>
                <option value="Sandstorms">Sandstorms (25.9m)</option>
                <option value="Windy">Windy (26.1m)</option>
              </select>
            </div>

            {/* Select 2: Traffic Density */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Traffic Congestion</label>
              <select
                value={params.traffic}
                onChange={(e) => setParams({ ...params, traffic: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500"
              >
                <option value="Low">Low (Free Flow: 21.5m)</option>
                <option value="Medium">Medium (26.7m)</option>
                <option value="High">High (27.2m)</option>
                <option value="Jam">Jam (Gridlock: 31.2m)</option>
              </select>
            </div>

            {/* Select 3: City Tier */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">City Tier</label>
              <select
                value={params.city}
                onChange={(e) => setParams({ ...params, city: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500"
              >
                <option value="Metropolitian">Metropolitan (77% orders)</option>
                <option value="Urban">Urban (Fastest: 23.0m)</option>
                <option value="Semi-Urban">Semi-Urban (49.7m)</option>
              </select>
            </div>

            {/* Select 4: Vehicle Modality */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Fleet Vehicle</label>
              <select
                value={params.vehicle}
                onChange={(e) => setParams({ ...params, vehicle: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500"
              >
                <option value="scooter">Scooter (24.5m)</option>
                <option value="electric_scooter">Electric Scooter (24.5m)</option>
                <option value="motorcycle">Motorcycle (27.6m)</option>
                <option value="bicycle">Bicycle (26.4m)</option>
              </select>
            </div>

            {/* Select 5: Multi-Order Batching */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Batched Stacked Orders</label>
              <select
                value={params.multiple_deliveries}
                onChange={(e) => setParams({ ...params, multiple_deliveries: parseInt(e.target.value) })}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500"
              >
                <option value="0">0 Batched (Solo Dispatch)</option>
                <option value="1">1 Batched Order (+3.8m vs solo)</option>
                <option value="2">2 Batched Orders (+17.6m vs solo)</option>
                <option value="3">3 Batched Orders (+24.9m vs solo)</option>
              </select>
            </div>

            {/* Select 6: Festival Status */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Festival Surge Status</label>
              <select
                value={params.festival}
                onChange={(e) => setParams({ ...params, festival: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500"
              >
                <option value="No">No (Standard SLA Day)</option>
                <option value="Yes">Yes (Holiday Surge: +19.6m)</option>
              </select>
            </div>

            {/* Slider 2: Hour of Day */}
            <div className="space-y-2 sm:col-span-2">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-slate-300">Order Dispatch Hour</span>
                <span className="font-mono font-bold text-amber-400">{params.hour}:00</span>
              </div>
              <input
                type="range"
                min="0"
                max="23"
                value={params.hour}
                onChange={(e) => setParams({ ...params, hour: parseInt(e.target.value) })}
                className="w-full accent-amber-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>00:00 (Midnight)</span>
                <span>13:00 (Lunch)</span>
                <span>20:00 (Dinner Peak)</span>
                <span>23:00 (Late Night)</span>
              </div>
            </div>

          </div>
        </div>

        {/* Right Column: Live Prediction Display + Order Preview */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Real-Time Result Gauge Card */}
          <div className="glass-panel-glow rounded-3xl p-7 border border-rose-500/30 text-center relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-rose-500 via-red-500 to-amber-500" />
            
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Random Forest Predicted ETA
            </span>

            <div className="my-5">
              <div className="text-6xl font-black text-white tracking-tight flex items-center justify-center gap-2">
                {loading ? (
                  <RefreshCw className="w-12 h-12 animate-spin text-rose-500" />
                ) : (
                  <>
                    <span>{prediction}</span>
                    <span className="text-2xl font-semibold text-rose-400">min</span>
                  </>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                Holdout error band (RMSE ±{(modelMetrics?.rmse ?? 4.03).toFixed(1)}m): [{prediction ? (prediction - (modelMetrics?.rmse ?? 4.03)).toFixed(1) : 0}m, {prediction ? (prediction + (modelMetrics?.rmse ?? 4.03)).toFixed(1) : 0}m]
              </p>
            </div>

            {/* SLA Status Pill */}
            {sla && SlaIcon && (
              <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold border ${sla.color} mb-4`}>
                <SlaIcon className="w-4 h-4" />
                <span>{sla.label}</span>
              </div>
            )}

            {/* Operational benchmarks mini grid (dataset group means) */}
            <div className="grid grid-cols-2 gap-2 text-left pt-3 border-t border-slate-800/80 text-xs">
              <div className="p-2 rounded-lg bg-slate-800/50">
                <span className="text-slate-400 block text-[10px]">Route Distance</span>
                <span className="font-bold text-white font-mono">{params.distance.toFixed(1)} km</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-800/50">
                <span className="text-slate-400 block text-[10px]">Traffic Benchmark</span>
                <span className="font-bold text-amber-400 font-mono">{TRAFFIC_BENCH[params.traffic]?.toFixed(2)}m avg</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-800/50">
                <span className="text-slate-400 block text-[10px]">Weather Benchmark</span>
                <span className="font-bold text-blue-400 font-mono">{WEATHER_BENCH[params.weather]?.toFixed(2)}m avg</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-800/50">
                <span className="text-slate-400 block text-[10px]">Batching Benchmark</span>
                <span className="font-bold text-rose-400 font-mono">{BATCH_BENCH[params.multiple_deliveries]?.toFixed(2)}m avg</span>
              </div>
            </div>
          </div>

          {/* Realistic Order Tracking Preview Card with Photo */}
          <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex items-center gap-4">
            <div className="w-20 h-20 rounded-xl overflow-hidden border border-slate-700 shrink-0">
              <img src={REAL_IMAGES.pizza} alt="Food Order" className="w-full h-full object-cover" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-white">Live Route Simulation</span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              </div>
              <p className="text-[11px] text-slate-400">
                Delivering via <strong className="text-white capitalize">{params.vehicle.replace('_', ' ')}</strong> in <strong className="text-white">{params.city}</strong>
              </p>
              <div className="text-[10px] text-slate-500 font-mono">
                Order Latency Buffer: {prediction && prediction > 30 ? `+${(prediction - 30).toFixed(1)}m added to app ETA` : 'Guaranteed On-Time'}
              </div>
            </div>
          </div>

        </div>

      </div>

      {/* 3. Syllabus Note on Machine Learning Role */}
      <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-start gap-3 text-xs text-slate-300">
        <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <strong className="text-white font-semibold">Coursework Compliance (Requirement 8):</strong>
          <p className="text-slate-400 leading-relaxed">
            As strictly mandated by the course faculty, this Machine Learning model serves exclusively as a <strong>supporting validation mechanism</strong> to corroborate the feature rankings uncovered in Requirement 2B (EDA) and Requirement 7 (Hypothesis Testing). The project centers on Foundations of Data Science, Central Limit Theorem statistics, and operational business decisions.
          </p>
        </div>
      </div>

    </div>
  )
}
