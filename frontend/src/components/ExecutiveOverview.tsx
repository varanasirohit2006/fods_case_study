import React from 'react'
import {
  KPIs,
  CityMetric,
  WeatherMetric,
  TrafficMetric,
} from '../types'
import { REAL_IMAGES } from '../data/mockData'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
} from 'recharts'
import {
  Clock,
  Users,
  Star,
  MapPin,
  TrendingUp,
  Package,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react'

interface ExecutiveOverviewProps {
  kpis: KPIs
  cityData: CityMetric[]
  weatherData: WeatherMetric[]
  trafficData: TrafficMetric[]
}

const CITY_COLORS = ['#e23744', '#f59e0b', '#3b82f6']

export const ExecutiveOverview: React.FC<ExecutiveOverviewProps> = ({
  kpis,
  cityData,
  weatherData,
  trafficData,
}) => {
  // Format city pie data
  const cityPieData = cityData.map((c) => ({
    name: c.city,
    value: c.order_count,
    time: c.mean_time,
  }))

  const trafficBy = (name: string) => trafficData.find((t) => t.traffic === name)?.mean_time
  const lowTraffic = trafficBy('Low')
  const jamTraffic = trafficBy('Jam')
  const jamDelta = lowTraffic !== undefined && jamTraffic !== undefined ? jamTraffic - lowTraffic : 9.7
  const fogMean = weatherData.find((w) => w.weather === 'Fog')?.mean_time
  const cloudyMean = weatherData.find((w) => w.weather === 'Cloudy')?.mean_time
  const wetWeatherMean = Math.max(fogMean ?? 28.7, cloudyMean ?? 28.9)

  return (
    <div className="space-y-8">
      {/* 1. Core Operational KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1: Total Orders */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 relative overflow-hidden group hover:border-rose-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Deliveries</span>
            <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 group-hover:scale-110 transition">
              <Package className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mt-3">
            {kpis.total_orders ? kpis.total_orders.toLocaleString() : '45,584'}
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-2">
            <span className="text-emerald-400 font-medium">Cleaned &amp; validated</span>
            <span>across {kpis.total_cities || 3} city tiers</span>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-rose-500 to-red-600 opacity-60" />
        </div>

        {/* KPI 2: Mean Delivery Duration */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 relative overflow-hidden group hover:border-amber-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Mean Delivery Time</span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 group-hover:scale-110 transition">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mt-3">
            {kpis.avg_delivery_time} <span className="text-lg font-medium text-slate-400">min</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-2">
            <span className="text-emerald-400 font-semibold">-3.71m faster</span>
            <span>than 30m SLA claim</span>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 to-orange-500 opacity-60" />
        </div>

        {/* KPI 3: Fleet Delivery Partners */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 relative overflow-hidden group hover:border-blue-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Fleet Size</span>
            <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 group-hover:scale-110 transition">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mt-3">
            {kpis.total_delivery_partners ? kpis.total_delivery_partners.toLocaleString() : '1,320'}
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-2">
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
            <span className="text-white font-semibold">{kpis.avg_rating} / 5.0</span>
            <span>fleet rating</span>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-cyan-500 opacity-60" />
        </div>

        {/* KPI 4: Mean Haversine Distance */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 relative overflow-hidden group hover:border-emerald-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Route Distance</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition">
              <MapPin className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mt-3">
            {kpis.avg_distance_km} <span className="text-lg font-medium text-slate-400">km</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-2">
            <span className="text-slate-300 font-medium">Median: {kpis.median_distance_km} km</span>
            <span>• P99: {kpis.p99_distance_km} km</span>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-60" />
        </div>

      </div>

      {/* 2. Charts Section: City Volume & Traffic Duration */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* City Tier Breakdown (Donut + Metric Table) */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 border border-slate-800/80">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">City Tier Distribution</h3>
              <p className="text-xs text-slate-400">Order share & transit latency by urban tier</p>
            </div>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              EDA 3
            </span>
          </div>

          <div className="h-52 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={cityPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {cityPieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={CITY_COLORS[index % CITY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const d = payload[0].payload
                      return (
                        <div className="glass-panel p-2.5 rounded-lg border border-slate-700 text-xs">
                          <div className="font-bold text-white">{d.name}</div>
                          <div className="text-rose-400 font-semibold">{d.value.toLocaleString()} orders</div>
                          <div className="text-slate-300">Mean SLA: {d.time} min</div>
                        </div>
                      )
                    }
                    return null
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* City Stats List */}
          <div className="space-y-2 mt-2 pt-3 border-t border-slate-800/80">
            {cityData.map((c, i) => (
              <div key={c.city} className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-800/40">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: CITY_COLORS[i] }} />
                  <span className="font-semibold text-slate-200">{c.city}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-400">{(c.order_count).toLocaleString()} orders</span>
                  <span className="font-bold text-white">{c.mean_time} min</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Traffic Density Impact Chart */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800/80">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Delivery Duration by Road Traffic Density</h3>
              <p className="text-xs text-slate-400">Monotonic congestion escalation from Low to Jam (EDA 7 & Q4)</p>
            </div>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
              Δ = +{jamDelta.toFixed(1)} min
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trafficData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="traffic" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[0, 40]} />
                <Tooltip
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const d = payload[0].payload as TrafficMetric
                      return (
                        <div className="glass-panel p-2.5 rounded-lg border border-slate-700 text-xs">
                          <div className="font-bold text-white">Traffic: {d.traffic}</div>
                          <div className="text-amber-400 font-semibold">Mean Time: {d.mean_time} min</div>
                          <div className="text-slate-400">Orders: {d.order_count.toLocaleString()}</div>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="mean_time" fill="#e23744" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 mt-3 pt-3 border-t border-slate-800/80">
            <span>Low Traffic: <strong>{trafficBy('Low')} min</strong></span>
            <span>Medium: <strong>{trafficBy('Medium')} min</strong></span>
            <span>High: <strong>{trafficBy('High')} min</strong></span>
            <span className="text-rose-400 font-bold">Jam: {trafficBy('Jam')} min</span>
          </div>
        </div>

      </div>

      {/* 3. Realistic Operational Imagery Gallery */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white">Operational Realities on the Ground</h3>
            <p className="text-xs text-slate-400">Real photographic documentation of transit environments in Indian logistics</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Photo Card 1: Traffic Rush */}
          <div className="rounded-2xl overflow-hidden glass-panel border border-slate-800 group hover:border-slate-700 transition">
            <div className="relative aspect-video overflow-hidden">
              <img
                src={REAL_IMAGES.heavyTraffic}
                alt="Heavy Traffic"
                className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
              />
              <span className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600/90 text-white shadow">
                Congestion Friction
              </span>
            </div>
            <div className="p-4 space-y-1.5">
              <h4 className="text-sm font-bold text-white">Peak Hour Jam Congestion</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Traffic Jams delay riders by <strong className="text-rose-400">+{jamDelta.toFixed(1)} min</strong> compared to free-flowing conditions.
              </p>
            </div>
          </div>

          {/* Photo Card 2: Rain & Monsoon */}
          <div className="rounded-2xl overflow-hidden glass-panel border border-slate-800 group hover:border-slate-700 transition">
            <div className="relative aspect-video overflow-hidden">
              <img
                src={REAL_IMAGES.rainDelivery}
                alt="Monsoon Delivery"
                className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
              />
              <span className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold bg-blue-600/90 text-white shadow">
                Weather Friction
              </span>
            </div>
            <div className="p-4 space-y-1.5">
              <h4 className="text-sm font-bold text-white">Fog & Monsoon Weather</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Cloudy &amp; Fog conditions stretch transit to <strong className="text-blue-400">{wetWeatherMean.toFixed(1)} min</strong>, requiring rain buffering.
              </p>
            </div>
          </div>

          {/* Photo Card 3: Cloud Kitchen Prep */}
          <div className="rounded-2xl overflow-hidden glass-panel border border-slate-800 group hover:border-slate-700 transition">
            <div className="relative aspect-video overflow-hidden">
              <img
                src={REAL_IMAGES.kitchenPrep}
                alt="Kitchen Preparation"
                className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
              />
              <span className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-600/90 text-white shadow">
                Kitchen Dispatch
              </span>
            </div>
            <div className="p-4 space-y-1.5">
              <h4 className="text-sm font-bold text-white">Order Preparation Latency</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Merchant food preparation averages <strong className="text-amber-400">9.6 min</strong> before partner pickup.
              </p>
            </div>
          </div>

          {/* Photo Card 4: Festival Surge */}
          <div className="rounded-2xl overflow-hidden glass-panel border border-slate-800 group hover:border-slate-700 transition">
            <div className="relative aspect-video overflow-hidden">
              <img
                src={REAL_IMAGES.festival}
                alt="Festival Delivery"
                className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
              />
              <span className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold bg-purple-600/90 text-white shadow">
                Surge Bottleneck
              </span>
            </div>
            <div className="p-4 space-y-1.5">
              <h4 className="text-sm font-bold text-white">Holiday & Festival Demand</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Festival orders experience dramatic spikes, surging to <strong className="text-purple-400">45.52 min</strong>.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
