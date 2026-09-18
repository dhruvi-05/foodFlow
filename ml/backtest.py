"""
Backtest Comparison Table Generator for WasteWise AI.
Compares Naive, 7-Day MA, Seasonal Baseline, and LightGBM Blended on the 30-day evaluation window.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.fn_plan.forecast import baseline_forecast, generate_forecast


def run_backtest():
    data_path = os.path.join(os.path.dirname(__file__), "data", "sales_history.csv")
    if not os.path.exists(data_path):
        from ml.generate_data import generate_synthetic_data
        df = generate_synthetic_data(180)
    else:
        df = pd.read_csv(data_path)

    df["date"] = pd.to_datetime(df["date"])
    max_date = df["date"].max()
    eval_start = max_date - pd.Timedelta(days=29)

    eval_df = df[df["date"] >= eval_start].copy()
    
    results = {
        "Naive (Yesterday)": {"errors": [], "sold": []},
        "7-Day Moving Avg": {"errors": [], "sold": []},
        "Seasonal Baseline (Same DOW x4)": {"errors": [], "sold": []},
        "LightGBM Blended (Shipped)": {"errors": [], "sold": []}
    }

    model_path = os.path.join(os.path.dirname(__file__), "..", "backend", "fn_plan", "model.txt")

    for idx, row in eval_df.iterrows():
        current_date = row["date"]
        dish_id = row["dish_id"]
        actual_sold = row["units_sold"]
        
        # History available up to day prior
        history_df = df[(df["dish_id"] == dish_id) & (df["date"] < current_date)].copy()
        if history_df.empty:
            continue

        # 1. Naive (yesterday's sales)
        naive_pred = float(history_df.sort_values("date").iloc[-1]["units_sold"])
        results["Naive (Yesterday)"]["errors"].append(abs(actual_sold - naive_pred))
        results["Naive (Yesterday)"]["sold"].append(actual_sold)

        # 2. 7-Day Moving Avg
        ma7_pred = float(history_df.sort_values("date").tail(7)["units_sold"].mean())
        results["7-Day Moving Avg"]["errors"].append(abs(actual_sold - ma7_pred))
        results["7-Day Moving Avg"]["sold"].append(actual_sold)

        # 3. Seasonal Baseline
        base_pred = baseline_forecast(history_df, dish_id, current_date)
        results["Seasonal Baseline (Same DOW x4)"]["errors"].append(abs(actual_sold - base_pred))
        results["Seasonal Baseline (Same DOW x4)"]["sold"].append(actual_sold)

        # 4. LightGBM Blended
        fcst, _, _, _, _, _ = generate_forecast(
            history_df=history_df,
            dish_id=dish_id,
            target_date=current_date,
            model_path=model_path,
            price=row["price"],
            promo=row["promotion"],
            temp=row["temperature"],
            rain=row["rainfall"],
            holiday=row["holiday"]
        )
        results["LightGBM Blended (Shipped)"]["errors"].append(abs(actual_sold - fcst))
        results["LightGBM Blended (Shipped)"]["sold"].append(actual_sold)

    print("\n" + "=" * 70)
    print("DEMO BACKTEST COMPARISON TABLE (Last 30 Days Validation Window)")
    print("=" * 70)
    print(f"{'Method':<35} | {'MAE (units)':<12} | {'MAPE (%)':<10}")
    print("-" * 70)

    for method, data in results.items():
        errs = np.array(data["errors"])
        solds = np.array(data["sold"])
        mae = np.mean(errs)
        mape = np.mean(errs / np.maximum(1, solds)) * 100.0
        print(f"{method:<35} | {mae:<12.2f} | {mape:<10.2f}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_backtest()
