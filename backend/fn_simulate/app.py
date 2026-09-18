"""
Interactive Walk-Forward Simulation Mode Handler for WasteWise AI (POST /api/simulate).
Compares naive manager baseline vs. WasteWise AI recommendations on held-out 30 days of history.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.common.responses import json_response, error_response
from backend.fn_plan.app import load_history_df, load_seed_data
from backend.fn_plan.forecast import generate_forecast
from backend.fn_plan.recommend import calculate_recommendation_and_risk

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "fn_plan", "model.txt")


def simulate_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    try:
        df = load_history_df()
        df["date"] = pd.to_datetime(df["date"])
        max_date = df["date"].max()
        eval_start = max_date - pd.Timedelta(days=29)

        dishes_list, _ = load_seed_data()
        dish_map = {d["dish_id"]: d for d in dishes_list}

        holdout_df = df[df["date"] >= eval_start].copy()

        acc = {
            "current": {"prep": 0, "sold": 0, "wasted": 0, "waste_cost": 0.0, "missed_rev": 0.0},
            "wastewise": {"prep": 0, "sold": 0, "wasted": 0, "waste_cost": 0.0, "missed_rev": 0.0}
        }

        # Held-out walk-forward backtest
        for day in holdout_df["date"].unique():
            prior_df = df[df["date"] < day].copy()
            day_df = holdout_df[holdout_df["date"] == day]

            for _, row in day_df.iterrows():
                d_id = row["dish_id"]
                dish_info = dish_map.get(d_id, {"price": row["price"], "unit_cost": row["unit_cost"], "batch_size": 1})
                price = dish_info["price"]
                unit_cost = dish_info["unit_cost"]
                margin = max(0.0, price - unit_cost)
                batch_size = dish_info.get("batch_size", 1)

                # True demand is units_sold (since on non-sellout days, demand = sold)
                actual_demand = int(row["units_sold"])
                
                # Manager baseline (from synthetic history)
                prep_mgr = int(row["units_prepared"])

                # WasteWise AI recommended prep: ML forecast + optimal Newsvendor buffer
                fcst, _, _, sigma, _, drivers = generate_forecast(
                    history_df=prior_df,
                    dish_id=d_id,
                    target_date=pd.to_datetime(day),
                    model_path=MODEL_PATH,
                    price=price,
                    promo=row["promotion"],
                    temp=row["temperature"],
                    rain=row["rainfall"],
                    holiday=row["holiday"]
                )
                
                # WasteWise optimizes prep to minimize combined waste + lost margin
                prep_ai_raw, _, _ = calculate_recommendation_and_risk(
                    forecast_units=fcst,
                    sigma_dish=sigma,
                    price=price,
                    unit_cost=unit_cost,
                    inventory=0,  # Snapshot evaluation
                    batch_size=batch_size,
                    trend_14d_pct=drivers.get("trend_14d_pct", 0.0)
                )
                # Ensure minimum coverage for high-demand items
                prep_ai = max(int(round(fcst * 1.04)), prep_ai_raw)

                # Reconstruct outcomes for both
                for label, prep in [("current", prep_mgr), ("wastewise", prep_ai)]:
                    sold = min(actual_demand, prep)
                    wasted = max(0, prep - sold)
                    missed = max(0, actual_demand - prep)

                    acc[label]["prep"] += prep
                    acc[label]["sold"] += sold
                    acc[label]["wasted"] += wasted
                    acc[label]["waste_cost"] += wasted * unit_cost
                    acc[label]["missed_rev"] += missed * margin

        # Deltas & net benefit
        current = acc["current"]
        wastewise = acc["wastewise"]

        waste_cost_saving = current["waste_cost"] - wastewise["waste_cost"]
        missed_rev_improvement = current["missed_rev"] - wastewise["missed_rev"]
        net_benefit = waste_cost_saving + missed_rev_improvement

        metrics_table = [
            {
                "metric": "Portions prepared",
                "current": int(current["prep"]),
                "wastewise": int(wastewise["prep"]),
                "delta": int(wastewise["prep"] - current["prep"])
            },
            {
                "metric": "Portions sold",
                "current": int(current["sold"]),
                "wastewise": int(wastewise["sold"]),
                "delta": int(wastewise["sold"] - current["sold"])
            },
            {
                "metric": "Portions wasted",
                "current": int(current["wasted"]),
                "wastewise": int(wastewise["wasted"]),
                "delta": int(wastewise["wasted"] - current["wasted"])
            },
            {
                "metric": "Waste cost (₹)",
                "current": int(round(current["waste_cost"])),
                "wastewise": int(round(wastewise["waste_cost"])),
                "delta": -int(round(waste_cost_saving))
            },
            {
                "metric": "Missed sales (₹)",
                "current": int(round(current["missed_rev"])),
                "wastewise": int(round(wastewise["missed_rev"])),
                "delta": -int(round(missed_rev_improvement))
            },
            {
                "metric": "Net benefit (₹ / 30 days)",
                "current": 0,
                "wastewise": int(round(net_benefit)),
                "delta": int(round(net_benefit))
            }
        ]

        response_body = {
            "evaluation_days": 30,
            "metrics": metrics_table,
            "headline_saving_rupees": int(round(net_benefit)),
            "waste_cost_reduction_pct": round((waste_cost_saving / max(1.0, current["waste_cost"])) * 100.0, 1),
            "mandatory_caption": "Simulated on 30 days of held-out historical data. Not a measured deployment result."
        }

        return json_response(200, response_body)

    except Exception as e:
        return error_response("INTERNAL", f"Server error: {str(e)}", status_code=500)
