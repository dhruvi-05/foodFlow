"use client";

import { useState } from "react";
import { ShoppingCart, ChevronDown, ChevronUp, AlertCircle, CheckCircle2 } from "lucide-react";
import { PurchaseListData } from "@/lib/api";

interface BuyListProps {
  data: PurchaseListData;
}

export default function BuyList({ data }: BuyListProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (!data || !data.purchase_list) return null;

  return (
    <div className="bg-slate-900/80 rounded-2xl border border-slate-800 shadow-xl overflow-hidden mb-8">
      {/* Panel Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 bg-slate-900 hover:bg-slate-800/60 transition-colors border-b border-slate-800"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <ShoppingCart className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-left">
            <h3 className="text-lg font-bold text-white tracking-tight">
              Ingredient Purchase List (Recipe Explosion)
            </h3>
            <p className="text-xs text-slate-400">
              Auto-calculated from tomorrow's prep plan minus current stock
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <span className="block text-xs font-medium text-slate-400">Total Est. Spend</span>
            <span className="text-xl font-extrabold text-amber-400">
              ₹{data.total_est_cost.toLocaleString()}
            </span>
          </div>
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          )}
        </div>
      </button>

      {/* Expandable Table Content */}
      {isOpen && (
        <div className="p-5">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800 bg-slate-950/40">
                <tr>
                  <th className="py-3 px-4">Ingredient</th>
                  <th className="py-3 px-4 text-right">Required (kg)</th>
                  <th className="py-3 px-4 text-right">In Stock (kg)</th>
                  <th className="py-3 px-4 text-right">Buy Qty (kg)</th>
                  <th className="py-3 px-4 text-right">Est. Cost (₹)</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium">
                {data.purchase_list.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-white">{item.ingredient}</td>
                    <td className="py-3.5 px-4 text-right">{item.required_kg.toFixed(2)}</td>
                    <td className="py-3.5 px-4 text-right text-slate-400">{item.in_stock_kg.toFixed(2)}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-amber-300">
                      {item.rounded_buy_kg > 0 ? item.rounded_buy_kg.toFixed(1) : "0.0"}
                    </td>
                    <td className="py-3.5 px-4 text-right font-semibold text-white">
                      ₹{item.est_cost.toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {item.urgent ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <AlertCircle className="w-3 h-3" />
                          URGENT
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-400">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          STABLE
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="border-t-2 border-slate-800 bg-slate-950/80 font-bold text-white">
                <tr>
                  <td className="py-4 px-4 text-emerald-400">TOTAL ESTIMATED PURCHASE</td>
                  <td className="py-4 px-4 text-right">
                    {data.purchase_list.reduce((acc, i) => acc + i.required_kg, 0).toFixed(2)} kg
                  </td>
                  <td className="py-4 px-4 text-right text-slate-400">
                    {data.purchase_list.reduce((acc, i) => acc + i.in_stock_kg, 0).toFixed(2)} kg
                  </td>
                  <td className="py-4 px-4 text-right text-amber-400">
                    {data.purchase_list.reduce((acc, i) => acc + i.rounded_buy_kg, 0).toFixed(1)} kg
                  </td>
                  <td className="py-4 px-4 text-right text-amber-400 text-base">
                    ₹{data.total_est_cost.toLocaleString()}
                  </td>
                  <td className="py-4 px-4 text-center text-xs text-slate-400">
                    {data.lines_sufficient} lines stocked
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
