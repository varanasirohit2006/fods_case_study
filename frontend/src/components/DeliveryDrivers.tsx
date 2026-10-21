import React, { useState } from 'react'
import {
  HourlyMetric,
  WeatherMetric,
  FestivalMetric,
  TopCombinations,
} from '../types'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Line,
  ComposedChart,
  ReferenceLine,
} from 'recharts'
import { Clock, Sun, CloudRain, Flame, AlertTriangle, CheckCircle, Compass } from 'lucide-react'

interface DeliveryDriversProps {
  hourlyData: HourlyMetric[]
  weatherData: WeatherMetric[]
  festivalData: FestivalMetric[]
  topCombinations: TopCombinations
}

export const DeliveryDrivers: React.FC<DeliveryDriversProps> = ({
  hourlyData,
  weatherData,
  festivalData,
  topCombinations,
}) => {
  const [combView, setCombView] = useState<'slowest' | 'fastest'>('slowest')

  // Weighted summaries so the headline cards always mirror the chart data.
  const windowStats = (lo: number, hi: number) => {
    const rows = hourlyData.filter((h) => h.hour >= lo && h.hour <= hi)
    const orders = rows.reduce((sum, h) => sum + h.order_count, 0)
    const weighted = rows.reduce((sum, h) => sum + h.mean_time * h.order_count, 0)
    return {
      perHour: rows.length ? Math.round(orders / rows.length) : 0,
      mean: orders ? weighted / orders : 0,
      max: rows.reduce((m, h) => Math.max(m, h.order_count), 0),
    }
  }
  const lunch = windowStats(12, 14)
  const dinner = windowStats(19, 21)
  const offPeak = windowStats(0, 9)

  const weatherBy = (name: string) => weatherData.find((w) => w.weather === name)?.mean_time
  const sunny = weatherBy('Sunny') ?? 21.86
  const fog = weatherBy('Fog') ?? 28.74
  const cloudy = weatherBy('Cloudy') ?? 28.92
  const weatherDelta = Math.max(fog, cloudy) - sunny

  const festivalYes = festivalData.find((f) => f.festival === 'Yes')
  const festivalNo = festivalData.find((f) => f.festival === 'No')
  const festYes = festivalYes?.mean_time ?? 45.52
  const festNo = festivalNo?.mean_time ?? 25.91
  const festDelta = festYes - festNo
  const festPct = festNo ? (festDelta / festNo) * 100 : 0
  const festRows = (festivalYes?.order_count ?? 0) + (festivalNo?.order_count ?? 0)
  const noShare = festRows ? ((festivalNo?.order_count ?? 0) / festRows) * 100 : 0

  return (
    <div className="space-y-8">
      
      {/* 1. Header explanation */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <Compass className="w-4 h-4" />
              <span>Analytical Deep-Dive • Requirements 4 & 5 (Q1–Q9)</span>
            </div>
            <h2 className="text-xl font-extrabold text-white">Delivery Time Drivers & Temporal Dynamics</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Deconstructing the exact friction points across hours of the day, environmental weather conditions, and festival surge shocks using statistical inference.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 font-medium border border-slate-700">
              CLT Z-Tests & Permutation Tested
            </span>
          </div>
        </div>
      </div>

      {/* 2. Hourly Dual-Axis Trend: Demand Spike vs SLA Latency */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h3 className="text-base font-bold text-white">Hourly Order Demand & Delivery Duration Curve</h3>
            <p className="text-xs text-slate-400">Order count volume (bars) vs. mean delivery latency (orange line) across 24 hours (Q7)</p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-3 rounded bg-rose-500/80 inline-block" /> Order Volume
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-1 bg-amber-400 inline-block" /> Mean Time (min)
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={hourlyData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="hour" stroke="#94a3b8" tickFormatter={(h) => `${h}:00`} tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis yAxisId="left" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis yAxisId="right" orientation="right" domain={[15, 35]} stroke="#f59e0b" tick={{ fill: '#f59e0b', fontSize: 11 }} />
              <Tooltip
                content={({ payload }) => {
                  if (payload && payload.length) {
                    const d = payload[0].payload as HourlyMetric
                    return (
                      <div className="glass-panel p-3 rounded-xl border border-slate-700 text-xs shadow-xl">
                        <div className="font-bold text-white mb-1">{d.hour}:00 - {d.hour}:59</div>
                        <div className="text-rose-400 font-semibold">{d.order_count.toLocaleString()} Orders</div>
                        <div className="text-amber-400 font-semibold">{d.mean_time} min Mean Delivery Time</div>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Bar yAxisId="left" dataKey="order_count" fill="#e23744" opacity={0.7} radius={[4, 4, 0, 0]} />
              <Line yAxisId="right" type="monotone" dataKey="mean_time" stroke="#f59e0b" strokeWidth={3} dot={{ r: 3, fill: '#f59e0b' }} />
              <ReferenceLine yAxisId="right" y={30} stroke="#ef4444" strokeDasharray="3 3" label={{ value: '30m SLA', fill: '#ef4444', fontSize: 10 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4 pt-4 border-t border-slate-800 text-xs">
          <div className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/50">
            <span className="text-slate-400 block font-medium">Lunch Peak (12:00 - 14:00)</span>
            <span className="text-white font-bold text-sm">~{lunch.perHour.toLocaleString()} orders/hr • {lunch.mean.toFixed(1)} min avg</span>
          </div>
          <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30">
            <span className="text-rose-400 block font-medium">Dinner Peak (19:00 - 21:00)</span>
            <span className="text-white font-bold text-sm">~{dinner.perHour.toLocaleString()} orders/hr • {dinner.mean.toFixed(1)} min avg</span>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/50">
            <span className="text-slate-400 block font-medium">Off-Peak (00:00 - 09:00)</span>
            <span className="text-white font-bold text-sm">≤{offPeak.max.toLocaleString()} orders/hr • {offPeak.mean.toFixed(1)} min avg</span>
          </div>
        </div>
      </div>

      {/* 3. Weather Conditions & Festival Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Weather Conditions Bar Chart */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Weather Condition Latency Profile</h3>
              <p className="text-xs text-slate-400">Atmospheric friction from Sunny to Fog & Cloudy (Q3)</p>
            </div>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
              Δ = +{weatherDelta.toFixed(2)} min
            </span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weatherData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="weather" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} domain={[15, 35]} />
                <Tooltip
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const d = payload[0].payload as WeatherMetric
                      return (
                        <div className="glass-panel p-2.5 rounded-lg border border-slate-700 text-xs">
                          <div className="font-bold text-white">{d.weather} Weather</div>
                          <div className="text-blue-400 font-semibold">{d.mean_time} min Mean Time</div>
                          <div className="text-slate-400">{d.order_count.toLocaleString()} Orders</div>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="mean_time" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                <ReferenceLine y={26.29} stroke="#10b981" strokeDasharray="3 3" label={{ value: 'Fleet Avg (26.3m)', fill: '#10b981', fontSize: 10 }} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800">
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <Sun className="w-3.5 h-3.5" /> Sunny: {sunny.toFixed(2)} min
            </span>
            <span className="flex items-center gap-1 text-blue-400 font-medium">
              <CloudRain className="w-3.5 h-3.5" /> Fog: {fog.toFixed(2)} min
            </span>
            <span className="flex items-center gap-1 text-slate-300 font-medium">
              Cloudy: {cloudy.toFixed(2)} min
            </span>
          </div>
        </div>

        {/* Festival Surge Impact Box */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white">Holiday & Festival Surge Shock</h3>
                <p className="text-xs text-slate-400">Two-Sample Z-Test: z = +139.68 (Q6 & Test 2)</p>
              </div>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30">
                p &lt; 1e-15
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 text-center">
                <span className="text-xs text-slate-400 block font-medium">Standard Non-Festival</span>
                <span className="text-2xl font-extrabold text-white mt-1 block">{festNo.toFixed(2)} <span className="text-xs font-normal text-slate-400">min</span></span>
                <span className="text-[10px] text-emerald-400 block mt-1">{(festivalNo?.order_count ?? 0).toLocaleString()} Orders ({noShare.toFixed(1)}%)</span>
              </div>

              <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-500/40 text-center relative overflow-hidden">
                <span className="text-xs text-purple-300 block font-medium">Festival Days</span>
                <span className="text-2xl font-extrabold text-purple-300 mt-1 block">{festYes.toFixed(2)} <span className="text-xs font-normal text-purple-400">min</span></span>
                <span className="text-[10px] text-rose-400 block mt-1">+{festDelta.toFixed(2)} min (+{festPct.toFixed(1)}%)</span>
                <div className="absolute top-1 right-1">
                  <Flame className="w-3.5 h-3.5 text-purple-400 animate-bounce" />
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/40 p-3 rounded-xl border border-slate-700/40">
              <strong className="text-purple-300">Statistical Finding:</strong> Festival orders average {festYes.toFixed(2)} min vs {festNo.toFixed(2)} min on normal days (+{festDelta.toFixed(2)} min, +{festPct.toFixed(1)}%), consistent with kitchen queue overload and partner scarcity. This supports <strong className="text-white">Decision 3</strong> (+30% active surge fleet deployment).
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Critical Value: z_crit = 1.96</span>
            <span className="text-emerald-400 font-semibold">Null Rejected (p &lt; 0.001)</span>
          </div>
        </div>

      </div>

      {/* 4. Multi-Factor Combinations Table (Slowest vs Fastest) */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-base font-bold text-white">Multi-Factor Interaction Extremes (City × Weather × Traffic)</h3>
            <p className="text-xs text-slate-400">Requirement 5: Identifying operational sweet-spots vs bottleneck combinations</p>
          </div>
          <div className="flex items-center gap-1 p-1 bg-slate-800 rounded-lg border border-slate-700">
            <button
              onClick={() => setCombView('slowest')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                combView === 'slowest' ? 'bg-rose-500 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              10 Slowest Combinations
            </button>
            <button
              onClick={() => setCombView('fastest')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                combView === 'fastest' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              10 Fastest Combinations
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold">
                <th className="py-2.5 px-3">#</th>
                <th className="py-2.5 px-3">City Tier</th>
                <th className="py-2.5 px-3">Weather</th>
                <th className="py-2.5 px-3">Traffic Condition</th>
                <th className="py-2.5 px-3">Order Count</th>
                <th className="py-2.5 px-3">Mean Time</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(combView === 'slowest' ? topCombinations.slowest_10 : topCombinations.fastest_10).map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition">
                  <td className="py-2 px-3 text-slate-500 font-mono">{idx + 1}</td>
                  <td className="py-2 px-3 font-semibold text-white">{row.city}</td>
                  <td className="py-2 px-3 text-slate-300">{row.weather}</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      row.traffic === 'Jam' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                      row.traffic === 'High' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                      row.traffic === 'Medium' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                      'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}>
                      {row.traffic}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-slate-400 font-mono">{row.order_count.toLocaleString()}</td>
                  <td className="py-2 px-3 font-bold text-white font-mono">{row.mean_time} min</td>
                  <td className="py-2 px-3">
                    {combView === 'slowest' ? (
                      <span className="flex items-center gap-1 text-rose-400 text-[11px]">
                        <AlertTriangle className="w-3 h-3" /> SLA Risk
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-emerald-400 text-[11px]">
                        <CheckCircle className="w-3 h-3" /> SLA Compliant
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  )
}
