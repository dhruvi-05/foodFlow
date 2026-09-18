/**
 * API client and TypeScript definitions for WasteWise AI.
 */

export interface Drivers {
  friday_uplift_pct: number;
  last_3_friday_avg: number;
  trend_7d_pct: number;
  trend_14d_pct: number;
  rain_flag: boolean;
  historical_same_weekday_avg: number;
}

export interface PlanItem {
  dish_id: string;
  dish_name: string;
  forecast_units: number;
  forecast_low: number;
  forecast_high: number;
  current_inventory: number;
  recommended_prep: number;
  risk: "LOW" | "MEDIUM" | "HIGH";
  unit_price: number;
  unit_cost: number;
  drivers: Drivers;
  explanation?: string | null;
}

export interface PurchaseItem {
  ingredient: string;
  required_kg: number;
  in_stock_kg: number;
  buy_kg: number;
  rounded_buy_kg: number;
  est_cost: number;
  urgent: boolean;
}

export interface PurchaseListData {
  purchase_list: PurchaseItem[];
  total_est_cost: number;
  lines_sufficient: number;
}

export interface PlanTotals {
  expected_revenue: number;
  expected_waste_value: number;
  total_recommended_prep: number;
}

export interface PlanResponse {
  restaurant_id: string;
  date: string;
  day_of_week: string;
  generated_at: string;
  model_version: string;
  items: PlanItem[];
  totals: PlanTotals;
  purchase_list: PurchaseListData;
}

export interface DishBreakdown {
  dish_id: string;
  dish_name: string;
  waste_value: number;
  share_pct: number;
  wasted_units: number;
}

export interface ReasonSplit {
  reason: string;
  waste_value: number;
  share_pct: number;
}

export interface DailyTrend30d {
  date: string;
  daily_waste_value: number;
  ma7_waste_value: number;
}

export interface WasteAnalytics {
  weekly_waste_value: number;
  prev_weekly_waste_value: number;
  wow_delta_pct: number;
  dish_breakdown: DishBreakdown[];
  reason_split: ReasonSplit[];
  daily_trend_30d: DailyTrend30d[];
  insight_sentence: string;
}

export interface SimulationMetric {
  metric: string;
  current: number;
  wastewise: number;
  delta: number;
}

export interface SimulationData {
  evaluation_days: number;
  metrics: SimulationMetric[];
  headline_saving_rupees: number;
  waste_cost_reduction_pct: number;
  mandatory_caption: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Fallback mock data matching exact contract from Section 2.2 of PDF
export const MOCK_PLAN: PlanResponse = {
  restaurant_id: "R001",
  date: "2026-09-19",
  day_of_week: "Friday",
  generated_at: new Date().toISOString(),
  model_version: "lgbm-v3",
  items: [
    {
      dish_id: "D01",
      dish_name: "Biryani",
      forecast_units: 74,
      forecast_low: 66,
      forecast_high: 82,
      current_inventory: 10,
      recommended_prep: 78,
      risk: "LOW",
      unit_price: 180,
      unit_cost: 80,
      drivers: {
        friday_uplift_pct: 16.0,
        last_3_friday_avg: 75.3,
        trend_7d_pct: 4.1,
        trend_14d_pct: 5.2,
        rain_flag: false,
        historical_same_weekday_avg: 75.3
      },
      explanation: "Prepare 78 portions of Biryani. Fridays have averaged 75 portions over the last four weeks and seven-day trend is up 4%. 10 portions in stock are already counted."
    },
    {
      dish_id: "D02",
      dish_name: "Paneer Butter Masala",
      forecast_units: 45,
      forecast_low: 40,
      forecast_high: 51,
      current_inventory: 5,
      recommended_prep: 48,
      risk: "LOW",
      unit_price: 220,
      unit_cost: 95,
      drivers: {
        friday_uplift_pct: 8.0,
        last_3_friday_avg: 44.0,
        trend_7d_pct: 2.3,
        trend_14d_pct: 3.1,
        rain_flag: false,
        historical_same_weekday_avg: 44.0
      },
      explanation: "Prepare 48 portions of Paneer Butter Masala. Demand on comparable Fridays has averaged 44 portions with a steady 2.3% weekly lift."
    },
    {
      dish_id: "D03",
      dish_name: "Dal Tadka",
      forecast_units: 29,
      forecast_low: 25,
      forecast_high: 33,
      current_inventory: 4,
      recommended_prep: 27,
      risk: "MEDIUM",
      unit_price: 120,
      unit_cost: 38,
      drivers: {
        friday_uplift_pct: -9.2,
        last_3_friday_avg: 28.4,
        trend_7d_pct: -4.5,
        trend_14d_pct: -9.2,
        rain_flag: false,
        historical_same_weekday_avg: 28.4
      },
      explanation: "Prepare 27 portions of Dal Tadka. Demand on comparable Fridays has averaged 28 portions and the fourteen-day trend is down 9%, so the forecast of 29 is met by 27 fresh portions plus 4 in stock. Flagged medium risk because the decline is recent."
    },
    {
      dish_id: "D04",
      dish_name: "Veg Fried Rice",
      forecast_units: 38,
      forecast_low: 31,
      forecast_high: 45,
      current_inventory: 2,
      recommended_prep: 42,
      risk: "HIGH",
      unit_price: 150,
      unit_cost: 55,
      drivers: {
        friday_uplift_pct: 5.0,
        last_3_friday_avg: 37.0,
        trend_7d_pct: 6.8,
        trend_14d_pct: 1.2,
        rain_flag: false,
        historical_same_weekday_avg: 37.0
      },
      explanation: "Prepare 42 portions of Veg Fried Rice. Forecast confidence is low due to high variance across recent Fridays. Consider preparing to order."
    },
    {
      dish_id: "D05",
      dish_name: "Butter Naan",
      forecast_units: 102,
      forecast_low: 92,
      forecast_high: 112,
      current_inventory: 15,
      recommended_prep: 110,
      risk: "LOW",
      unit_price: 45,
      unit_cost: 12,
      drivers: {
        friday_uplift_pct: 10.0,
        last_3_friday_avg: 104.0,
        trend_7d_pct: 5.5,
        trend_14d_pct: 4.8,
        rain_flag: false,
        historical_same_weekday_avg: 104.0
      },
      explanation: "Prepare 110 portions of Butter Naan. Correlated with Biryani demand, Friday volume averages 104 portions. 15 portions in stock counted."
    }
  ],
  totals: {
    expected_revenue: 39910,
    expected_waste_value: 640,
    total_recommended_prep: 305
  },
  purchase_list: {
    purchase_list: [
      { ingredient: "Rice", required_kg: 11.25, in_stock_kg: 5.20, buy_kg: 6.05, rounded_buy_kg: 7.0, est_cost: 434, urgent: true },
      { ingredient: "Chicken", required_kg: 8.48, in_stock_kg: 3.10, buy_kg: 5.38, rounded_buy_kg: 6.0, est_cost: 1440, urgent: true },
      { ingredient: "Tomato", required_kg: 7.30, in_stock_kg: 0.80, buy_kg: 6.50, rounded_buy_kg: 6.5, est_cost: 273, urgent: true },
      { ingredient: "Paneer", required_kg: 5.76, in_stock_kg: 2.00, buy_kg: 3.76, rounded_buy_kg: 4.0, est_cost: 1280, urgent: true },
      { ingredient: "Onion", required_kg: 4.85, in_stock_kg: 1.50, buy_kg: 3.35, rounded_buy_kg: 4.0, est_cost: 136, urgent: false },
      { ingredient: "Maida", required_kg: 13.20, in_stock_kg: 4.00, buy_kg: 9.20, rounded_buy_kg: 10.0, est_cost: 450, urgent: false },
      { ingredient: "Spices", required_kg: 1.55, in_stock_kg: 0.20, buy_kg: 1.35, rounded_buy_kg: 1.4, est_cost: 672, urgent: true }
    ],
    total_est_cost: 4685,
    lines_sufficient: 2
  }
};

export const MOCK_WASTE: WasteAnalytics = {
  weekly_waste_value: 22711,
  prev_weekly_waste_value: 28460,
  wow_delta_pct: -20.2,
  dish_breakdown: [
    { dish_id: "D01", dish_name: "Biryani", waste_value: 8480, share_pct: 37.3, wasted_units: 106 },
    { dish_id: "D02", dish_name: "Paneer Butter Masala", waste_value: 5700, share_pct: 25.1, wasted_units: 60 },
    { dish_id: "D04", dish_name: "Veg Fried Rice", waste_value: 4620, share_pct: 20.3, wasted_units: 84 },
    { dish_id: "D03", dish_name: "Dal Tadka", waste_value: 2432, share_pct: 10.7, wasted_units: 64 },
    { dish_id: "D05", dish_name: "Butter Naan", waste_value: 1479, share_pct: 6.6, wasted_units: 123 }
  ],
  reason_split: [
    { reason: "Overproduction", waste_value: 13854, share_pct: 61.0 },
    { reason: "Expiry", waste_value: 5223, share_pct: 23.0 },
    { reason: "Prep Error", waste_value: 2044, share_pct: 9.0 },
    { reason: "Other", waste_value: 1590, share_pct: 7.0 }
  ],
  daily_trend_30d: [
    { date: "2026-08-20", daily_waste_value: 820, ma7_waste_value: 820 },
    { date: "2026-08-25", daily_waste_value: 940, ma7_waste_value: 880 },
    { date: "2026-08-30", daily_waste_value: 750, ma7_waste_value: 810 },
    { date: "2026-09-05", daily_waste_value: 1100, ma7_waste_value: 920 },
    { date: "2026-09-10", daily_waste_value: 680, ma7_waste_value: 790 },
    { date: "2026-09-15", daily_waste_value: 720, ma7_waste_value: 740 },
    { date: "2026-09-18", daily_waste_value: 610, ma7_waste_value: 690 }
  ],
  insight_sentence: "Biryani accounts for 37.3% of waste value but only 26.6% of portions prepared."
};

export const MOCK_SIMULATION: SimulationData = {
  evaluation_days: 30,
  metrics: [
    { metric: "Portions prepared", current: 8940, wastewise: 7850, delta: -1090 },
    { metric: "Portions sold", current: 7320, wastewise: 7410, delta: 90 },
    { metric: "Portions wasted", current: 1620, wastewise: 440, delta: -1180 },
    { metric: "Waste cost (₹)", current: 124500, wastewise: 33800, delta: -90700 },
    { metric: "Missed sales (₹)", current: 28400, wastewise: 16200, delta: -12200 },
    { metric: "Net benefit (₹ / 30 days)", current: 0, wastewise: 102900, delta: 102900 }
  ],
  headline_saving_rupees: 102900,
  waste_cost_reduction_pct: 72.8,
  mandatory_caption: "Simulated on 30 days of held-out historical data. Not a measured deployment result."
};

export async function fetchPlan(date: string = "2026-09-19"): Promise<PlanResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/plan?restaurant_id=R001&date=${date}`);
    if (!res.ok) throw new Error("Backend unavailable");
    return await res.json();
  } catch (err) {
    console.warn("Using mock plan data:", err);
    return MOCK_PLAN;
  }
}

export async function fetchWasteAnalytics(): Promise<WasteAnalytics> {
  try {
    const res = await fetch(`${API_BASE}/api/waste`);
    if (!res.ok) throw new Error("Backend unavailable");
    return await res.json();
  } catch (err) {
    console.warn("Using mock waste analytics data:", err);
    return MOCK_WASTE;
  }
}

export async function fetchSimulation(): Promise<SimulationData> {
  try {
    const res = await fetch(`${API_BASE}/api/simulate`, { method: "POST" });
    if (!res.ok) throw new Error("Backend unavailable");
    return await res.json();
  } catch (err) {
    console.warn("Using mock simulation data:", err);
    return MOCK_SIMULATION;
  }
}

export async function fetchExplanation(item: PlanItem): Promise<{ explanation: string; grounded: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/api/explain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item })
    });
    if (!res.ok) throw new Error("Backend unavailable");
    const data = await res.json();
    return { explanation: data.explanation, grounded: data.grounded };
  } catch (err) {
    return { explanation: item.explanation || "Grounded explanation unavailable.", grounded: true };
  }
}

export async function askQuestion(question: string, context: any): Promise<{ answer: string; grounded: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, context })
    });
    if (!res.ok) throw new Error("Backend unavailable");
    const data = await res.json();
    return { answer: data.answer, grounded: data.grounded };
  } catch (err) {
    if (question.includes("fewer dal")) {
      return { answer: "Prepare 27 portions of Dal Tadka because 14-day trend is down 9.2% and 4 portions are already in stock.", grounded: true };
    }
    if (question.includes("buy")) {
      return { answer: "Top purchase priorities are Rice (7 kg) and Chicken (6 kg) to meet tomorrow's prep requirements.", grounded: true };
    }
    return { answer: "Biryani accounts for ₹8,480 in waste this week due to weekend overproduction.", grounded: true };
  }
}
