import React, { useState, useEffect } from 'react'
import { FilteredOrder } from '../types'
import { fetchFilteredOrders } from '../api'
import { Table, Filter, Search, RefreshCw, ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react'

export const DataExplorer: React.FC = () => {
  const [city, setCity] = useState<string>('All')
  const [weather, setWeather] = useState<string>('All')
  const [traffic, setTraffic] = useState<string>('All')
  const [vehicle, setVehicle] = useState<string>('All')
  const [searchTerm, setSearchTerm] = useState<string>('')

  const [orders, setOrders] = useState<FilteredOrder[]>([])
  const [totalCount, setTotalCount] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(false)
  const [isLive, setIsLive] = useState<boolean>(false)

  // Pagination
  const [currentPage, setCurrentPage] = useState<number>(1)
  const pageSize = 8

  // Load orders when filters change
  useEffect(() => {
    let active = true
    const loadOrders = async () => {
      setLoading(true)
      const res = await fetchFilteredOrders({
        city,
        weather,
        traffic,
        vehicle,
        search: searchTerm,
      })
      if (active) {
        setOrders(res.data.data)
        setTotalCount(res.data.total_matching)
        setIsLive(res.isLive)
        setCurrentPage(1)
        setLoading(false)
      }
    }
    // Debounce keystrokes so search hits the API instead of the 1,000-row cap.
    const timer = setTimeout(loadOrders, 350)
    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [city, weather, traffic, vehicle, searchTerm])

  // Paginated slice over the returned rows (server searches before the 1,000-row cap)
  const paginatedOrders = orders.slice((currentPage - 1) * pageSize, currentPage * pageSize)
  const totalPages = Math.ceil(orders.length / pageSize) || 1

  // Mean SLA of the returned subset
  const subsetAvg = orders.length
    ? (orders.reduce((acc, curr) => acc + curr.Time_taken_min, 0) / orders.length).toFixed(1)
    : '0'

  return (
    <div className="space-y-6">
      
      {/* 1. Header Banner */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <Table className="w-4 h-4" />
              <span>Full-Stack Integration • Endpoint /api/filtered-data</span>
            </div>
            <h2 className="text-xl font-extrabold text-white">Interactive Operational Dataset Explorer</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Query the cleaned 45,584 delivery transactions in real-time. Apply multi-dimensional parametric filters across city, weather, traffic congestion, and fleet vehicles.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${
              isLive ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-300 border-slate-700'
            }`}>
              {isLive ? 'Live API Querying' : 'Local Verified Cache'}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Filter Bar Matrix */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
            <Filter className="w-3.5 h-3.5 text-rose-500" />
            Query Filters
          </div>
          
          {/* Search box */}
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search Order ID / Partner ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          {/* City Filter */}
          <div className="space-y-1">
            <label className="text-slate-400 font-medium">City Tier</label>
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-rose-500"
            >
              <option value="All">All Cities</option>
              <option value="Metropolitian">Metropolitan</option>
              <option value="Urban">Urban</option>
              <option value="Semi-Urban">Semi-Urban</option>
            </select>
          </div>

          {/* Weather Filter */}
          <div className="space-y-1">
            <label className="text-slate-400 font-medium">Weather Condition</label>
            <select
              value={weather}
              onChange={(e) => setWeather(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-rose-500"
            >
              <option value="All">All Weather</option>
              <option value="Sunny">Sunny</option>
              <option value="Cloudy">Cloudy</option>
              <option value="Fog">Fog</option>
              <option value="Stormy">Stormy</option>
              <option value="Sandstorms">Sandstorms</option>
              <option value="Windy">Windy</option>
            </select>
          </div>

          {/* Traffic Filter */}
          <div className="space-y-1">
            <label className="text-slate-400 font-medium">Traffic Density</label>
            <select
              value={traffic}
              onChange={(e) => setTraffic(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-rose-500"
            >
              <option value="All">All Traffic</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Jam">Jam</option>
            </select>
          </div>

          {/* Vehicle Filter */}
          <div className="space-y-1">
            <label className="text-slate-400 font-medium">Vehicle Modality</label>
            <select
              value={vehicle}
              onChange={(e) => setVehicle(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-rose-500"
            >
              <option value="All">All Vehicles</option>
              <option value="scooter">Scooter</option>
              <option value="electric_scooter">Electric Scooter</option>
              <option value="motorcycle">Motorcycle</option>
              <option value="bicycle">Bicycle</option>
            </select>
          </div>
        </div>

        {/* Filter Stats Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-800 text-xs">
          <div className="flex items-center gap-4 text-slate-300">
            <span>
              Matching Orders: <strong className="text-white font-mono">{totalCount.toLocaleString()}</strong>
            </span>
            <span>
              Subset Mean SLA: <strong className="text-rose-400 font-mono">{subsetAvg} min</strong>
            </span>
          </div>

          <button
            onClick={() => {
              setCity('All')
              setWeather('All')
              setTraffic('All')
              setVehicle('All')
              setSearchTerm('')
            }}
            className="text-xs text-slate-400 hover:text-white transition cursor-pointer"
          >
            Clear All Filters
          </button>
        </div>
      </div>

      {/* 3. Transaction Data Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-semibold">
              <tr>
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Delivery Partner</th>
                <th className="py-3 px-4">City</th>
                <th className="py-3 px-4">Weather</th>
                <th className="py-3 px-4">Traffic</th>
                <th className="py-3 px-4">Vehicle</th>
                <th className="py-3 px-4">Batched</th>
                <th className="py-3 px-4">Rating</th>
                <th className="py-3 px-4">Delivery SLA</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto text-rose-500 mb-2" />
                    Querying records...
                  </td>
                </tr>
              ) : paginatedOrders.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    No orders match the selected filter criteria.
                  </td>
                </tr>
              ) : (
                paginatedOrders.map((order, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-bold text-white">{order.ID}</td>
                    <td className="py-3 px-4 text-slate-300 font-sans">{order.Delivery_person_ID}</td>
                    <td className="py-3 px-4 text-slate-300 font-sans">{order.City}</td>
                    <td className="py-3 px-4 text-slate-300 font-sans">{order.Weather}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-sans font-semibold ${
                        order.Traffic === 'Jam' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                        order.Traffic === 'High' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                        order.Traffic === 'Medium' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                        'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      }`}>
                        {order.Traffic}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-sans capitalize">{order.Vehicle_type.replace('_', ' ')}</td>
                    <td className="py-3 px-4 text-slate-400">
                      {order.multiple_deliveries === 0 ? 'Solo' : `${order.multiple_deliveries} Batched`}
                    </td>
                    <td className="py-3 px-4 text-amber-400 font-bold">{order.Rating} ★</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        order.Time_taken_min <= 25 ? 'bg-emerald-500/20 text-emerald-300' :
                        order.Time_taken_min <= 35 ? 'bg-amber-500/20 text-amber-300' :
                        'bg-rose-500/20 text-rose-300'
                      }`}>
                        {order.Time_taken_min} min
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing {orders.length === 0 ? 0 : (currentPage - 1) * pageSize + 1} - {Math.min(currentPage * pageSize, orders.length)} of {totalCount.toLocaleString()} matching records
            {totalCount > orders.length ? ` (first ${orders.length.toLocaleString()} loaded)` : ''}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-white">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>

    </div>
  )
}
