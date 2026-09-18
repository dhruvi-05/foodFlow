"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sparkles, BarChart3, Calculator, Calendar } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Tomorrow's Plan", icon: Calendar },
    { href: "/waste", label: "Waste Analytics", icon: BarChart3 },
    { href: "/simulate", label: "Simulation Mode", icon: Calculator },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-950/80 border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-0.5 shadow-lg shadow-emerald-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  WasteWise AI
                </span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  MVP R001
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium hidden sm:block">
                Restaurant Demand Forecasting & Food-Waste Reduction
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800/60">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all duration-200 ${
                    isActive
                      ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm shadow-emerald-500/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Live AWS Infrastructure Status Badge */}
          <div className="hidden lg:flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>AWS us-east-1 | DynamoDB + Bedrock</span>
          </div>
        </div>
      </div>
    </header>
  );
}
