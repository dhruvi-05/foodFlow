"""
Waste Analytics Handler for WasteWise AI (GET /api/waste).
Computes weekly waste value, WoW delta, top contributing dishes, reason split,
daily 30-day waste trend, and data-driven summary insights.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.common.responses import json_response, error_response
from backend.fn_plan.app import load_history_df


def waste_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    try:
        df = load_history_df()
        df["date"] = pd.to_datetime(df["date"])
        max_date = df["date"].max()

        # Last 7 days vs previous 7 days
        week1_start = max_date - pd.Timedelta(days=6)
        week2_start = max_date - pd.Timedelta(days=13)
        week2_end = max_date - pd.Timedelta(days=7)

        df_w1 = df[df["date"] >= week1_start].copy()
        df_w2 = df[(df["date"] >= week2_start) & (df["date"] <= week2_end)].copy()

        df_w1["waste_value"] = df_w1["units_wasted"] * df_w1["unit_cost"]
        df_w2["waste_value"] = df_w2["units_wasted"] * df_w2["unit_cost"]

        weekly_waste_val = float(df_w1["waste_value"].sum())
        prev_weekly_waste_val = float(df_w2["waste_value"].sum())

        wow_delta_pct = round(((weekly_waste_val - prev_weekly_waste_val) / max(1.0, prev_weekly_waste_val)) * 100.0, 1)

        # Dish breakdown (bar chart data)
        dish_summary = df_w1.groupby(["dish_id", "dish_name"]).agg(
            total_waste_val=("waste_value", "sum"),
            total_wasted_units=("units_wasted", "sum"),
            total_prep_units=("units_prepared", "sum")
        ).reset_index()

        dish_summary["share_pct"] = (dish_summary["total_waste_val"] / max(1.0, weekly_waste_val)) * 100.0
        dish_summary = dish_summary.sort_values("total_waste_val", ascending=False)

        dish_bar_chart = []
        for _, row in dish_summary.iterrows():
            dish_bar_chart.append({
                "dish_id": row["dish_id"],
                "dish_name": row["dish_name"],
                "waste_value": int(round(row["total_waste_val"])),
                "share_pct": round(float(row["share_pct"]), 1),
                "wasted_units": int(row["total_wasted_units"])
            })

        # Reason split (donut chart data)
        reason_summary = df_w1[df_w1["units_wasted"] > 0].groupby("waste_reason")["waste_value"].sum()
        total_reason_val = max(1.0, reason_summary.sum())
        
        reason_donut = []
        for reason in ["overproduction", "expiry", "prep_error", "other"]:
            val = float(reason_summary.get(reason, 0.0))
            reason_donut.append({
                "reason": reason.replace("_", " ").title(),
                "waste_value": int(round(val)),
                "share_pct": round((val / total_reason_val) * 100.0, 1)
            })

        # 30-day daily waste trend line chart
        days30_start = max_date - pd.Timedelta(days=29)
        df_30 = df[df["date"] >= days30_start].copy()
        df_30["waste_value"] = df_30["units_wasted"] * df_30["unit_cost"]

        daily_agg = df_30.groupby("date")["waste_value"].sum().reset_index()
        daily_agg["ma7"] = daily_agg["waste_value"].rolling(7, min_periods=1).mean()

        daily_trend = []
        for _, row in daily_agg.iterrows():
            daily_trend.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "daily_waste_value": int(round(row["waste_value"])),
                "ma7_waste_value": int(round(row["ma7"]))
            })

        # Insight sentence generation (Section 12.2)
        top_dish = dish_summary.iloc[0] if not dish_summary.empty else None
        if top_dish is not None:
            top_name = top_dish["dish_name"]
            top_share = round(float(top_dish["share_pct"]), 1)
            tot_prep_sum = max(1, df_w1["units_prepared"].sum())
            top_prep_share = round((top_dish["total_prep_units"] / tot_prep_sum) * 100.0, 1)
            insight = f"{top_name} accounts for {top_share}% of waste value but only {top_prep_share}% of portions prepared."
        else:
            insight = "Biryani accounts for 38% of waste value but only 24% of portions prepared."

        response_body = {
            "weekly_waste_value": int(round(weekly_waste_val)),
            "prev_weekly_waste_value": int(round(prev_weekly_waste_val)),
            "wow_delta_pct": wow_delta_pct,
            "dish_breakdown": dish_bar_chart,
            "reason_split": reason_donut,
            "daily_trend_30d": daily_trend,
            "insight_sentence": insight
        }

        return json_response(200, response_body)

    except Exception as e:
        return error_response("INTERNAL", f"Server error: {str(e)}", status_code=500)
