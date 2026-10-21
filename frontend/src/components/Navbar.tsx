import React from 'react'
import { Activity, RefreshCw, Database, Sparkles, Truck, BarChart3, Sliders, Table, Compass } from 'lucide-react'

interface NavbarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  isLive: boolean
  isLoading: boolean
  onRefresh: () => void
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  isLive,
  isLoading,
  onRefresh,
}) => {
  const tabs = [
    { id: 'overview', label: 'Overview & KPIs', icon: BarChart3 },
    { id: 'drivers', label: 'Delivery Time Drivers', icon: Activity },
    { id: 'fleet', label: 'Fleet & Partner Intel', icon: Truck },
    { id: 'predictor', label: 'AI ETA Predictor', icon: Sparkles },
    { id: 'explorer', label: 'Dataset Explorer', icon: Table },
    { id: 'decisions', label: 'Strategic Playbook', icon: Compass },
  ]

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand identity */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center shadow-lg shadow-rose-900/40">
              <span className="text-white font-extrabold text-xl tracking-tighter">Z</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg text-white tracking-tight">zomato</span>
                <span className="text-xs font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  Analytics
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">FoDS 23CSE351 Operations Intelligence</p>
            </div>
          </div>

          {/* Backend Status indicator */}
          <div className="flex items-center gap-2 md:hidden">
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
              isLive ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              {isLive ? 'API Live' : 'Cached Data'}
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center gap-1 overflow-x-auto max-w-full pb-1 md:pb-0 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs lg:text-sm font-semibold transition-all whitespace-nowrap cursor-pointer ${
                  isActive
                    ? 'bg-rose-500 text-white shadow-md shadow-rose-600/30 scale-[1.02]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                {tab.label}
              </button>
            )
          })}
        </nav>

        {/* Actions & Status Desktop */}
        <div className="hidden md:flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
            isLive 
              ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30' 
              : 'bg-amber-950/40 text-amber-300 border-amber-500/30'
          }`}>
            <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`} />
            <Database className="w-3.5 h-3.5 opacity-70" />
            <span>{isLive ? 'Flask API (5000)' : 'FoDS Cache (45.5k)'}</span>
          </div>

          <button
            onClick={onRefresh}
            disabled={isLoading}
            title="Reload live metrics from backend"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-700/80 hover:text-white border border-slate-700 transition cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-rose-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>
    </header>
  )
}
