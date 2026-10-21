import React from 'react'
import { Sparkles, Clock, ShieldCheck, ArrowRight, Zap } from 'lucide-react'
import { REAL_IMAGES } from '../data/mockData'

interface HeroBannerProps {
  onExploreDrivers: () => void
  onOpenPredictor: () => void
}

export const HeroBanner: React.FC<HeroBannerProps> = ({
  onExploreDrivers,
  onOpenPredictor,
}) => {
  return (
    <section className="relative overflow-hidden rounded-3xl mb-8 border border-slate-800/80 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950">
      {/* Background ambient lighting */}
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-rose-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-red-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto p-6 lg:p-10 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Column: Headlines & Insights */}
          <div className="lg:col-span-7 space-y-5">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/25 text-rose-400 text-xs font-semibold">
              <Zap className="w-3.5 h-3.5" />
              <span>Foundation of Data Science Case Study • Academic Year 2026</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-[1.15]">
              Real-Time Delivery Operations &{' '}
              <span className="gradient-text-zomato">Statistical SLA Optimization</span>
            </h1>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl">
              Analyzing <strong className="text-white font-semibold">45,584 real Indian food delivery transactions</strong> across 3 city tiers (Metropolitan, Urban, Semi-Urban). Leveraging parametric Z-testing, non-parametric permutation resampling, and Machine Learning to isolate transit friction and cut customer wait times.
            </p>

            {/* Metric pill row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="text-slate-400 text-[11px] font-medium uppercase tracking-wider">Dataset Size</div>
                <div className="text-xl font-bold text-white mt-0.5">45,584</div>
                <div className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1 font-medium">
                  <ShieldCheck className="w-3 h-3" /> 100% Verified
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="text-slate-400 text-[11px] font-medium uppercase tracking-wider">Baseline SLA</div>
                <div className="text-xl font-bold text-white mt-0.5">26.29 <span className="text-xs font-normal text-slate-400">min</span></div>
                <div className="text-[10px] text-rose-400 flex items-center gap-1 mt-1 font-medium">
                  <Clock className="w-3 h-3" /> Claimed: 30 min
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="text-slate-400 text-[11px] font-medium uppercase tracking-wider">ML Accuracy</div>
                <div className="text-xl font-bold text-white mt-0.5">81.58% <span className="text-xs font-normal text-slate-400">R²</span></div>
                <div className="text-[10px] text-indigo-400 flex items-center gap-1 mt-1 font-medium">
                  <Sparkles className="w-3 h-3" /> Random Forest (API holdout)
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="text-slate-400 text-[11px] font-medium uppercase tracking-wider">Peak Dinner SLA</div>
                <div className="text-xl font-bold text-amber-300 mt-0.5">31.1 <span className="text-xs font-normal text-slate-400">min</span></div>
                <div className="text-[10px] text-amber-400 flex items-center gap-1 mt-1 font-medium">
                  <Clock className="w-3 h-3" /> 7–9 PM • +11.5 vs AM
                </div>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={onOpenPredictor}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-red-500 hover:from-rose-500 hover:to-red-400 text-white font-semibold text-sm shadow-lg shadow-rose-900/40 transition transform active:scale-95 cursor-pointer"
              >
                <Sparkles className="w-4 h-4" />
                <span>Simulate AI Delivery ETA</span>
              </button>

              <button
                onClick={onExploreDrivers}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 font-medium text-sm border border-slate-700 transition cursor-pointer"
              >
                <span>View Operational Drivers</span>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </button>
            </div>
          </div>

          {/* Right Column: Realistic Imagery Collage */}
          <div className="lg:col-span-5 relative">
            <div className="relative mx-auto max-w-md lg:max-w-none">
              
              {/* Main Realistic Hero Image: Delivery Rider */}
              <div className="relative rounded-2xl overflow-hidden border-2 border-slate-700/70 shadow-2xl shadow-black/80 aspect-[4/3] group">
                <img
                  src={REAL_IMAGES.heroRider}
                  alt="Zomato Real Delivery Partner"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />
                
                {/* Floating badge bottom left */}
                <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between p-2.5 rounded-xl glass-panel border border-white/10">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg overflow-hidden border border-white/20">
                      <img src={REAL_IMAGES.deliveryScooter} alt="Scooter" className="w-full h-full object-cover" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white flex items-center gap-1">
                        Active Fleet Partner
                        <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
                      </div>
                      <div className="text-[10px] text-slate-300">Scooter Fleet • Rating 4.8★</div>
                    </div>
                  </div>
                  <span className="text-xs font-bold text-rose-400 bg-rose-500/20 px-2 py-0.5 rounded border border-rose-500/30">
                    24.5m SLA
                  </span>
                </div>
              </div>

              {/* Floating Realistic Food Badge (Biryani / Gourmet Delivery) */}
              <div className="absolute -bottom-6 -left-6 hidden sm:flex items-center gap-3 p-2.5 rounded-2xl glass-panel-glow border border-rose-500/30 max-w-xs shadow-xl backdrop-blur-md">
                <img
                  src={REAL_IMAGES.biryani}
                  alt="Fresh Delivery"
                  className="w-12 h-12 rounded-xl object-cover border border-white/20"
                />
                <div>
                  <div className="text-xs font-bold text-white">Cloud Kitchen Dispatch</div>
                  <div className="text-[10px] text-slate-400">Prep: ~9.6 min • In Transit</div>
                </div>
              </div>

              {/* Top right pill: Peak hour signal */}
              <div className="absolute -top-3 -right-3 flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-700/80 text-amber-300 text-xs font-semibold shadow-lg backdrop-blur-md">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                <span>Dinner Surge Peak (7–9 PM)</span>
              </div>

            </div>
          </div>

        </div>
      </div>
    </section>
  )
}
