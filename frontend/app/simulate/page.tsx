"use client";

import { useState, useEffect } from "react";
import { Calculator, TrendingUp, CheckCircle, ShieldAlert, Sparkles } from "lucide-react";
import { fetchSimulation, SimulationData, MOCK_SIMULATION } from "@/lib/api";

export default function SimulationPage() {
  const [sim, setSim] = useState<SimulationData | null>(null);

  useEffect(() => {
    fetchSimulation()
      .then(setSim)
      .catch(() => setSim(MOCK_SIMULATION));
  }, []);

  const data = sim || MOCK_SIMULATION;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-black text-white tracking-tight">Walk-Forward Simulation Mode</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              30-Day Held-out Test
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Strict walk-forward backtest comparing Manager baseline vs. WasteWise AI recommendations
          </p>
        </div>

        {/* Headline Rupee Benefit Banner */}
        <div className="bg-gradient-to-r from-emerald-500/20 via-teal-500/10 to-transparent border border-emerald-500/30 p-4 rounded-xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <span className="block text-xs font-semibold text-emerald-400 uppercase tracking-wider">
              Net 30-Day Simulated Benefit
            </span>
            <span className="text-3xl font-black text-white tracking-tight">
              ₹{data.headline_saving_rupees.toLocaleString()}
            </span>
            <span className="block text-xs text-emerald-300 font-medium">
              {data.waste_cost_reduction_pct}% waste cost reduction achieved
            </span>
          </div>
        </div>
      </div>

      {/* Side-by-Side Comparison Table */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white">Manager Baseline vs. WasteWise AI Performance</h3>
            <p className="text-xs text-slate-400">Evaluated across {data.evaluation_days} held-out days without future data leakage</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800 bg-slate-950/40">
              <tr>
                <th className="py-3.5 px-4">Metric</th>
                <th className="py-3.5 px-4 text-right">Current Approach (Manager)</th>
                <th className="py-3.5 px-4 text-right text-emerald-400">WasteWise AI</th>
                <th className="py-3.5 px-4 text-right">Delta / Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {data.metrics.map((row, idx) => {
                const isHighlightRow = row.metric.includes("Net benefit");
                const isWasteCost = row.metric.includes("Waste cost");

                return (
                  <tr
                    key={idx}
                    className={`hover:bg-slate-800/30 transition-colors ${
                      isHighlightRow ? "bg-emerald-500/10 font-bold text-white text-base" : ""
                    }`}
                  >
                    <td className="py-4 px-4 font-semibold text-slate-100 flex items-center gap-2">
                      {isHighlightRow && <TrendingUp className="w-4 h-4 text-emerald-400" />}
                      {row.metric}
                    </td>

                    <td className="py-4 px-4 text-right text-slate-400">
                      {row.metric.includes("₹") ? `₹${row.current.toLocaleString()}` : row.current.toLocaleString()}
                    </td>

                    <td
                      className={`py-4 px-4 text-right font-extrabold ${
                        isHighlightRow ? "text-emerald-400 text-lg" : "text-slate-100"
                      }`}
                    >
                      {row.metric.includes("₹") ? `₹${row.wastewise.toLocaleString()}` : row.wastewise.toLocaleString()}
                    </td>

                    <td className="py-4 px-4 text-right font-bold">
                      {row.delta < 0 ? (
                        <span className="text-emerald-400">
                          {row.metric.includes("₹") ? `-₹${Math.abs(row.delta).toLocaleString()}` : row.delta}
                        </span>
                      ) : row.delta > 0 ? (
                        <span className="text-emerald-400">
                          +{row.metric.includes("₹") ? `₹${row.delta.toLocaleString()}` : row.delta}
                        </span>
                      ) : (
                        <span className="text-slate-500">0</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mandatory Honesty Framing Caption (Section 13.3) */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
        <div>
          <span className="block text-xs font-bold uppercase tracking-wider text-amber-400">
            Mandatory Demo Caption
          </span>
          <p className="text-sm font-medium text-amber-200">
            "{data.mandatory_caption}"
          </p>
        </div>
      </div>
    </div>
  );
}
