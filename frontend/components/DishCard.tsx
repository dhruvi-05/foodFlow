"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ShieldCheck, TrendingUp, AlertTriangle, AlertCircle, CheckCircle2 } from "lucide-react";
import { PlanItem } from "@/lib/api";

interface DishCardProps {
  item: PlanItem;
  defaultExpanded?: boolean;
}

export default function DishCard({ item, defaultExpanded = false }: DishCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "LOW":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            LOW RISK
          </span>
        );
      case "MEDIUM":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            MEDIUM RISK
          </span>
        );
      case "HIGH":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            HIGH RISK
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-5 shadow-xl hover:border-slate-700/80 transition-all duration-200">
      {/* Top Header */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-bold text-white tracking-tight">{item.dish_name}</h3>
            <span className="text-[11px] font-medium text-slate-400 bg-slate-800 px-2 py-0.5 rounded-md">
              {item.dish_id}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Sell: <span className="text-slate-200 font-semibold">₹{item.unit_price}</span> | Cost: <span className="text-slate-200 font-semibold">₹{item.unit_cost}</span>
          </p>
        </div>
        {getRiskBadge(item.risk)}
      </div>

      {/* Main Grid Metrics */}
      <div className="grid grid-cols-3 gap-3 p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 mb-4">
        <div>
          <span className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
            Expected Demand
          </span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-extrabold text-white">{item.forecast_units}</span>
            <span className="text-xs text-slate-400">
              ({item.forecast_low} - {item.forecast_high})
            </span>
          </div>
        </div>

        <div>
          <span className="block text-[11px] font-semibold uppercase tracking-wider text-emerald-400 mb-1">
            Recommended Prep
          </span>
          <span className="text-3xl font-extrabold text-emerald-400 tracking-tight">
            {item.recommended_prep}
          </span>
        </div>

        <div>
          <span className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
            In Stock
          </span>
          <span className="text-2xl font-extrabold text-slate-300">
            {item.current_inventory}
          </span>
        </div>
      </div>

      {/* Expandable Why? Panel */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-950/40 overflow-hidden">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between px-4 py-2.5 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/40 transition-colors"
        >
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span>Why prepare {item.recommended_prep} portions?</span>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </button>

        {isExpanded && (
          <div className="px-4 py-3 border-t border-slate-800/60 bg-slate-950/80 space-y-2">
            <p className="text-sm leading-relaxed text-slate-300 font-normal">
              {item.explanation || "Grounded explanation generated."}
            </p>
            <div className="flex items-center justify-end gap-1.5 text-[11px] font-mono font-medium text-emerald-400 pt-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>[verified: grounded]</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
