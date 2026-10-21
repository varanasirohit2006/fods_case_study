import React from 'react'
import { DecisionItem } from '../types'
import { Compass, CheckCircle2, TrendingUp, AlertCircle, ShieldCheck } from 'lucide-react'

interface StrategicDecisionsProps {
  decisions: DecisionItem[]
}

export const StrategicDecisions: React.FC<StrategicDecisionsProps> = ({ decisions }) => {
  return (
    <div className="space-y-8">
      
      {/* 1. Header Banner */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <Compass className="w-4 h-4" />
              <span>Requirement 6: Evidence-Based Decisions & Policy Playbooks</span>
            </div>
            <h2 className="text-xl font-extrabold text-white">7 Executive Operational Decisions</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Translating data analysis questions Q1–Q15 and formal hypothesis testing into concrete logistical interventions across surge pricing, routing algorithms, fleet modality, and rider allocation.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 text-xs font-semibold border border-rose-500/20">
              Validated Across 45,584 Orders
            </span>
          </div>
        </div>
      </div>

      {/* 2. Decisions Card Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {decisions.map((decision) => (
          <div
            key={decision.id}
            className="glass-panel rounded-3xl border border-slate-800 overflow-hidden flex flex-col justify-between group hover:border-slate-700 transition"
          >
            {/* Real photo banner with overlay tag */}
            {decision.image && (
              <div className="relative aspect-[16/8] overflow-hidden">
                <img
                  src={decision.image}
                  alt={decision.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />
                
                <div className="absolute top-3 left-3 flex items-center gap-2">
                  <span className="w-7 h-7 rounded-xl bg-rose-600 text-white font-extrabold text-xs flex items-center justify-center shadow-lg">
                    #{decision.id}
                  </span>
                  {decision.tag && (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-900/90 text-rose-300 border border-rose-500/30 backdrop-blur-md">
                      {decision.tag}
                    </span>
                  )}
                </div>
              </div>
            )}

            <div className="p-6 space-y-4 flex-1 flex flex-col justify-between">
              <div className="space-y-2">
                <h3 className="text-base font-bold text-white group-hover:text-rose-400 transition">
                  {decision.title}
                </h3>

                {/* Evidence block */}
                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-300 leading-relaxed space-y-1">
                  <div className="font-semibold text-slate-400 uppercase tracking-wider text-[10px] flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    Analytical Evidence:
                  </div>
                  <p>{decision.evidence}</p>
                </div>
              </div>

              {/* Impact pill */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center gap-2 text-xs">
                <TrendingUp className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="text-slate-300">
                  <strong className="text-emerald-400">Impact: </strong>
                  {decision.impact}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  )
}
