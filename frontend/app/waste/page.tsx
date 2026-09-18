"use client";

import { useState, useEffect } from "react";
import { TrendingDown, ArrowDownRight, Lightbulb, PieChart as PieIcon, BarChart3, LineChart as LineIcon } from "lucide-react";
import { fetchWasteAnalytics, WasteAnalytics, MOCK_WASTE } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, LineChart, Line, CartesianGrid, Legend
} from "recharts";

const REASON_COLORS: Record<string, string> = {
  Overproduction: "#ef4444", // Red
  Expiry: "#f59e0b",         // Amber
  "Prep Error": "#3b82f6",   // Blue
  Other: "#6b7280"           // Gray
};

const DISH_COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899"];

export default function WasteAnalyticsPage() {
  const [data, setData] = useState<WasteAnalytics | null>(null);

  useEffect(() => {
    fetchWasteAnalytics()
      .then(setData)
      .catch(() => setData(MOCK_WASTE));
  }, []);

  const wasteData = data || MOCK_WASTE;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Title & Hero Stat */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Waste Analytics</h1>
          <p className="text-sm text-slate-400">
            Root-cause breakdown and historical food waste financial tracking
          </p>
        </div>

        {/* Hero Weekly Waste Stat */}
        <div className="flex items-center gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div>
            <span className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">Weekly Waste Value</span>
            <span className="text-3xl font-black text-rose-400 tracking-tight">
              ₹{wasteData.weekly_waste_value.toLocaleString()}
            </span>
          </div>

          <div className="flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
            <ArrowDownRight className="w-4 h-4" />
            <span>{Math.abs(wasteData.wow_delta_pct)}% WoW</span>
          </div>
        </div>
      </div>

      {/* Insight Sentence Callout */}
      <div className="p-4 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center gap-3">
        <Lightbulb className="w-5 h-5 text-teal-400 shrink-0" />
        <p className="text-sm font-semibold text-teal-200">
          {wasteData.insight_sentence}
        </p>
      </div>

      {/* Grid: Bar Chart & Donut Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart: Waste by Dish */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-emerald-400" />
              <h3 className="text-base font-bold text-white">Waste Value by Dish (₹)</h3>
            </div>
            <span className="text-xs text-slate-400">Descending Share %</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={wasteData.dish_breakdown} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="dish_name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", color: "#fff" }}
                  formatter={(value: any) => [`₹${value}`, "Waste Value"]}
                />
                <Bar dataKey="waste_value" radius={[6, 6, 0, 0]}>
                  {wasteData.dish_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={DISH_COLORS[index % DISH_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Donut Chart: Waste Reason Split */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <PieIcon className="w-5 h-5 text-amber-400" />
              <h3 className="text-base font-bold text-white">Waste Reason Breakdown</h3>
            </div>
            <span className="text-xs text-slate-400">Categorized Split</span>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={wasteData.reason_split}
                  dataKey="waste_value"
                  nameKey="reason"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                >
                  {wasteData.reason_split.map((entry, index) => (
                    <Cell key={`pie-cell-${index}`} fill={REASON_COLORS[entry.reason] || "#6b7280"} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", color: "#fff" }}
                  formatter={(value: any) => [`₹${value}`, "Value"]}
                />
                <Legend formatter={(value) => <span className="text-xs text-slate-300 font-medium">{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 30-Day Waste Trend Line Chart */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LineIcon className="w-5 h-5 text-teal-400" />
            <h3 className="text-base font-bold text-white">30-Day Daily Waste Trend (₹)</h3>
          </div>
          <span className="text-xs text-slate-400">Daily Value + 7-Day Moving Average Overlay</span>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={wasteData.daily_trend_30d} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", color: "#fff" }}
              />
              <Legend />
              <Line type="monotone" dataKey="daily_waste_value" name="Daily Waste (₹)" stroke="#f43f5e" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ma7_waste_value" name="7-Day Moving Avg (₹)" stroke="#14b8a6" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
