"""
Synthetic Dataset Generator for WasteWise AI.
Generates 180 days of realistic daily sales history for 5 dishes (~900 rows).
Includes weather, seasonality, trend, holidays, promotions, and naive manager behavior.
"""

import os
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

DISHES = [
    {"dish_id": "D01", "dish_name": "Biryani", "category": "Main", "price": 180, "unit_cost": 80, "base_demand": 70, "trend_slope": 0.10},
    {"dish_id": "D02", "dish_name": "Paneer Butter Masala", "category": "Main", "price": 220, "unit_cost": 95, "base_demand": 42, "trend_slope": 0.00},
    {"dish_id": "D03", "dish_name": "Dal Tadka", "category": "Side", "price": 120, "unit_cost": 38, "base_demand": 32, "trend_slope": -0.12},
    {"dish_id": "D04", "dish_name": "Veg Fried Rice", "category": "Main", "price": 150, "unit_cost": 55, "base_demand": 36, "trend_slope": 0.00},
    {"dish_id": "D05", "dish_name": "Butter Naan", "category": "Bread", "price": 45, "unit_cost": 12, "base_demand": 95, "trend_slope": 0.00},
]

DOW_FACTORS = {
    "D01": [0.79, 0.81, 0.84, 0.89, 1.09, 1.30, 1.20],  # Mon=0..Sun=6
    "D02": [0.88, 0.90, 0.92, 0.95, 1.08, 1.20, 1.14],
    "D03": [1.06, 1.00, 0.97, 0.94, 0.91, 1.09, 1.19],
    "D04": [0.92, 0.95, 0.98, 1.00, 1.05, 1.12, 1.05],
    "D05": [0.87, 0.89, 0.93, 0.96, 1.10, 1.22, 1.16],
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def generate_weather_and_holidays(num_days: int, start_date: datetime):
    np.random.seed(42)
    rainfall = np.zeros(num_days)
    
    # Generate monsoon blocks (~18% rain days clustered in 3-5 day blocks)
    block_starts = [15, 28, 45, 62, 80, 105, 130, 155]
    for start in block_starts:
        duration = np.random.randint(3, 6)
        for d in range(start, min(num_days, start + duration)):
            rainfall[d] = np.random.uniform(6.0, 35.0)

    # Smooth seasonal temperature curve + noise
    temperature = np.zeros(num_days)
    for t in range(num_days):
        base_temp = 32.0 + 8.0 * math.sin(2 * math.pi * t / 180.0)
        noise = np.random.normal(0, 1.5)
        temperature[t] = round(max(15.0, min(45.0, base_temp + noise)), 1)

    # 6 Seeded Holidays across 180 days
    holiday_indices = set([20, 52, 90, 115, 142, 170])
    holidays = [1 if i in holiday_indices else 0 for i in range(num_days)]

    return rainfall, temperature, holidays


def generate_synthetic_data(num_days: int = 180, end_date: datetime = None) -> pd.DataFrame:
    if end_date is None:
        end_date = datetime(2026, 9, 18)
    
    start_date = end_date - timedelta(days=num_days - 1)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    rainfall, temperature, holidays = generate_weather_and_holidays(num_days, start_date)
    
    rows = []
    np.random.seed(42)

    # We track 7-day moving average of sold for naive manager preparation rule
    recent_sold = {d["dish_id"]: [] for d in DISHES}

    for day_idx, current_date in enumerate(dates):
        date_str = current_date.strftime("%Y-%m-%d")
        dow_idx = current_date.weekday()
        day_of_week = DAY_NAMES[dow_idx]
        is_holiday = holidays[day_idx]
        temp = temperature[day_idx]
        rain = rainfall[day_idx]
        rain_flag = rain > 5.0

        for dish in DISHES:
            d_id = dish["dish_id"]
            base = dish["base_demand"]
            dow_factor = DOW_FACTORS[d_id][dow_idx]
            trend_factor = 1.0 + dish["trend_slope"] * (day_idx / 180.0)
            seasonal_factor = 1.0 + 0.06 * math.sin(2 * math.pi * day_idx / 30.0)
            holiday_factor = 1.35 if is_holiday else 1.0
            
            # Promotions: ~15% of days for D02 & D04
            is_promo = 1 if (d_id in ["D02", "D04"] and (day_idx % 7 == 2 or day_idx % 11 == 0)) else 0
            promo_factor = 1.25 if is_promo == 1 else 1.0
            
            # Weather factors
            weather_factor = 1.0
            if rain_flag:
                if dish["category"] == "Main":
                    weather_factor *= 0.82
                elif dish["category"] == "Bread":
                    weather_factor *= 0.90
            
            if temp > 36.0:
                if d_id == "D01":
                    weather_factor *= 0.94
                elif d_id in ["D03", "D04"]:
                    weather_factor *= 1.05

            noise = np.random.lognormal(mean=0, sigma=0.08)
            true_demand = max(5, int(round(base * dow_factor * trend_factor * seasonal_factor * holiday_factor * promo_factor * weather_factor * noise)))

            # Naive Manager Preparation Rule: 1.18 * moving average of sold adjusted for weekday lift
            history = recent_sold[d_id]
            if len(history) < 7:
                avg_sold = base * dow_factor
            else:
                avg_sold = np.mean(history[-7:]) * dow_factor
            
            # Over-prepares by ~18% with slight batching
            prep_target = max(10, int(round(avg_sold * 1.20)))
            if dish["dish_id"] == "D01":  # Biryani batch of 5
                prepared = int(math.ceil(prep_target / 5.0) * 5)
            elif dish["dish_id"] == "D05":  # Naan batch of 10
                prepared = int(math.ceil(prep_target / 10.0) * 10)
            else:
                prepared = prep_target

            opening_inv = np.random.choice([0, 2, 4], p=[0.7, 0.2, 0.1])
            available = prepared + opening_inv
            
            # Observed sales (censored demand)
            sold = min(true_demand, available)
            wasted = max(0, available - sold)
            closing_inv = max(0, available - sold) if wasted == 0 else 0
            
            # Reason distribution
            if wasted > 0:
                waste_reason = np.random.choice(
                    ["overproduction", "expiry", "prep_error", "other"],
                    p=[0.61, 0.23, 0.09, 0.07]
                )
            else:
                waste_reason = "none"

            recent_sold[d_id].append(sold)

            rows.append({
                "date": date_str,
                "restaurant_id": "R001",
                "dish_id": d_id,
                "dish_name": dish["dish_name"],
                "category": dish["category"],
                "price": dish["price"],
                "unit_cost": dish["unit_cost"],
                "promotion": is_promo,
                "day_of_week": day_of_week,
                "holiday": is_holiday,
                "temperature": temp,
                "rainfall": rain,
                "units_prepared": prepared,
                "units_sold": sold,
                "units_wasted": wasted,
                "waste_reason": waste_reason,
                "opening_inventory": opening_inv,
                "closing_inventory": closing_inv,
            })

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = generate_synthetic_data(180)
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "sales_history.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} rows of synthetic data -> {csv_path}")
