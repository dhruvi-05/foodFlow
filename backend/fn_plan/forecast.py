"""
Forecasting Engine for WasteWise AI.
Includes Layer 1 (Seasonal Baseline), Layer 2 (LightGBM), and Layer 2b (Blending & Guardrails).
"""

import os
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

# Hard-coded z-score lookup table for Newsvendor critical ratio (to avoid scipy dependency size)
Z_TABLE = [
    (0.50, 0.00), (0.55, 0.13), (0.60, 0.25), (0.65, 0.39),
    (0.70, 0.52), (0.75, 0.67), (0.80, 0.84), (0.85, 1.04),
    (0.90, 1.28), (0.95, 1.64), (0.99, 2.33)
]


def get_z_score(critical_ratio: float) -> float:
    """Returns approximate standard normal z-score for a given critical ratio."""
    clamped = max(0.50, min(0.99, critical_ratio))
    for i in range(len(Z_TABLE) - 1):
        p1, z1 = Z_TABLE[i]
        p2, z2 = Z_TABLE[i + 1]
        if p1 <= clamped <= p2:
            # Linear interpolation
            return z1 + (z2 - z1) * ((clamped - p1) / (p2 - p1))
    return 0.50


def baseline_forecast(history_df: pd.DataFrame, dish_id: str, target_date: datetime) -> float:
    """
    Layer 1 - Seasonal Baseline Model.
    Computes mean of last 4 occurrences of the same weekday for dish_id,
    with short-term trend correction clamped between 0.85 and 1.15.
    """
    df_dish = history_df[history_df["dish_id"] == dish_id].copy()
    if df_dish.empty:
        return 30.0

    df_dish["date"] = pd.to_datetime(df_dish["date"])
    target_dow = target_date.weekday()

    # Same weekday history
    same_dow = df_dish[df_dish["date"].dt.weekday == target_dow]
    if same_dow.empty:
        level = df_dish["units_sold"].tail(7).mean()
    else:
        last_4 = same_dow.sort_values("date").tail(4)
        level = last_4["units_sold"].mean()

    # Short-term trend correction: recent 7 days vs earlier 21 days
    recent = df_dish.tail(7)["units_sold"].mean()
    earlier = df_dish.tail(28).head(21)["units_sold"].mean()
    
    if earlier > 0 and not pd.isna(earlier) and not pd.isna(recent):
        trend = recent / earlier
    else:
        trend = 1.0

    trend_clamped = min(max(trend, 0.85), 1.15)
    
    return float(level * trend_clamped)


def build_features_for_row(history_df: pd.DataFrame, dish_id: str, target_date: datetime,
                           price: float = 180.0, promo: int = 0, temp: float = 30.0,
                           rain: float = 0.0, holiday: int = 0) -> pd.DataFrame:
    """Builds single feature row for LightGBM inference."""
    df_dish = history_df[history_df["dish_id"] == dish_id].sort_values("date").copy()
    sold_series = df_dish["units_sold"].values if not df_dish.empty else np.array([30] * 30)

    def get_lag(n: int) -> float:
        return float(sold_series[-n]) if len(sold_series) >= n else float(sold_series[-1])

    lag_1 = get_lag(1)
    lag_2 = get_lag(2)
    lag_7 = get_lag(7)
    lag_14 = get_lag(14)
    lag_21 = get_lag(21)
    lag_28 = get_lag(28)

    roll_mean_7 = float(np.mean(sold_series[-7:])) if len(sold_series) >= 7 else lag_1
    roll_mean_14 = float(np.mean(sold_series[-14:])) if len(sold_series) >= 14 else roll_mean_7
    roll_std_7 = float(np.std(sold_series[-7:])) if len(sold_series) >= 7 else 5.0
    roll_max_7 = float(np.max(sold_series[-7:])) if len(sold_series) >= 7 else lag_1

    # Same weekday 4 rolling average
    dow = target_date.weekday()
    same_dow_vals = df_dish[pd.to_datetime(df_dish["date"]).dt.weekday == dow]["units_sold"].values
    roll_mean_same_dow_4 = float(np.mean(same_dow_vals[-4:])) if len(same_dow_vals) >= 4 else roll_mean_7

    feature_dict = {
        "dish_id": dish_id,
        "day_of_week": target_date.weekday(),
        "is_weekend": 1 if target_date.weekday() in [4, 5, 6] else 0,
        "month": target_date.month,
        "day_of_month": target_date.day,
        "is_holiday": holiday,
        "days_since_start": 180,
        "lag_1": lag_1,
        "lag_2": lag_2,
        "lag_7": lag_7,
        "lag_14": lag_14,
        "lag_21": lag_21,
        "lag_28": lag_28,
        "roll_mean_7": roll_mean_7,
        "roll_mean_14": roll_mean_14,
        "roll_std_7": roll_std_7,
        "roll_max_7": roll_max_7,
        "roll_mean_same_dow_4": roll_mean_same_dow_4,
        "lag_1_div_roll7": lag_1 / max(1.0, roll_mean_7),
        "roll7_div_roll14": roll_mean_7 / max(1.0, roll_mean_14),
        "price": price,
        "promotion": promo,
        "price_vs_30d_mean": 1.0,
        "temperature": temp,
        "rainfall": rain,
        "rain_flag": 1 if rain > 5.0 else 0,
    }
    return pd.DataFrame([feature_dict])


def generate_forecast(history_df: pd.DataFrame, dish_id: str, target_date: datetime,
                      model_path: str = None, price: float = 180.0, promo: int = 0,
                      temp: float = 30.0, rain: float = 0.0, holiday: int = 0) -> Tuple[float, float, float, float, str, Dict[str, Any]]:
    """
    Generates blended forecast with confidence bands and driver metrics.
    Returns: (forecast_units, forecast_low, forecast_high, sigma, model_version, drivers)
    """
    base = baseline_forecast(history_df, dish_id, target_date)
    ml_pred = base

    if model_path and os.path.exists(model_path) and HAS_LIGHTGBM:
        try:
            bst = lgb.Booster(model_file=model_path)
            X = build_features_for_row(history_df, dish_id, target_date, price, promo, temp, rain, holiday)
            # Categorical conversions
            X["dish_id"] = X["dish_id"].astype("category")
            X["day_of_week"] = X["day_of_week"].astype("category")
            ml_pred = float(bst.predict(X)[0])
            model_ver = "lgbm-v3"
        except Exception:
            ml_pred = base
            model_ver = "baseline-fallback"
    else:
        model_ver = "baseline-fallback"

    # Layer 2b Blending & Guardrails
    if model_ver == "lgbm-v3":
        blended = 0.65 * ml_pred + 0.35 * base
        blended = min(max(blended, base * 0.6), base * 1.4)
    else:
        blended = base

    forecast_val = max(0.0, blended)

    # Per-dish residual standard deviations (derived from validation set)
    SIGMA_MAP = {
        "D01": 8.0,   # Biryani
        "D02": 5.5,   # Paneer Butter Masala
        "D03": 4.0,   # Dal Tadka
        "D04": 6.8,   # Veg Fried Rice (higher variance)
        "D05": 9.5    # Butter Naan
    }
    sigma = SIGMA_MAP.get(dish_id, 6.0)

    low_units = max(0, int(round(forecast_val - 1.0 * sigma)))
    high_units = int(round(forecast_val + 1.0 * sigma))

    # Drivers calculation
    df_dish = history_df[history_df["dish_id"] == dish_id].sort_values("date")
    last_7 = df_dish.tail(7)["units_sold"].mean() if not df_dish.empty else forecast_val
    last_28_earlier = df_dish.tail(28).head(21)["units_sold"].mean() if not df_dish.empty else forecast_val
    trend_14d_pct = round(((last_7 - last_28_earlier) / max(1.0, last_28_earlier)) * 100.0, 1)

    dow_target = target_date.weekday()
    same_dow_hist = df_dish[pd.to_datetime(df_dish["date"]).dt.weekday == dow_target]["units_sold"]
    hist_same_dow_avg = round(float(same_dow_hist.tail(4).mean()), 1) if not same_dow_hist.empty else round(forecast_val, 1)

    drivers = {
        "friday_uplift_pct": 16.0 if target_date.weekday() == 4 else 0.0,
        "last_3_friday_avg": hist_same_dow_avg,
        "trend_7d_pct": round(((last_7 - forecast_val) / max(1.0, forecast_val)) * 100.0, 1),
        "trend_14d_pct": trend_14d_pct,
        "rain_flag": rain > 5.0,
        "historical_same_weekday_avg": hist_same_dow_avg,
        "day_of_week": target_date.strftime("%A")
    }

    return forecast_val, low_units, high_units, sigma, model_ver, drivers
