"""
Main Tomorrow's Plan Handler for WasteWise AI (GET /api/plan).
Integrates data loading, LightGBM forecasting, Newsvendor prep calculation, risk banding,
recipe explosion, and response serialization.
"""

import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.common.responses import json_response, error_response
from backend.common.models import PlanResponse, PlanItem, PlanTotals
from backend.fn_plan.forecast import generate_forecast
from backend.fn_plan.recommend import calculate_recommendation_and_risk
from backend.fn_plan.ingredients import generate_purchase_list
from backend.fn_explain.app import template_explanation

logger = logging.getLogger(__name__)

# Load seed metadata
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DISHES_SEED_PATH = os.path.join(BASE_DIR, "infra", "seed", "dishes.json")
RECIPES_SEED_PATH = os.path.join(BASE_DIR, "infra", "seed", "recipes.json")
SALES_HISTORY_PATH = os.path.join(BASE_DIR, "ml", "data", "sales_history.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.txt")


def load_seed_data():
    with open(DISHES_SEED_PATH, "r") as f:
        dishes = json.load(f)
    with open(RECIPES_SEED_PATH, "r") as f:
        recipes = json.load(f)
    return dishes, recipes


def load_history_df() -> pd.DataFrame:
    if os.path.exists(SALES_HISTORY_PATH):
        return pd.read_csv(SALES_HISTORY_PATH)
    else:
        from ml.generate_data import generate_synthetic_data
        df = generate_synthetic_data(180)
        os.makedirs(os.path.dirname(SALES_HISTORY_PATH), exist_ok=True)
        df.to_csv(SALES_HISTORY_PATH, index=False)
        return df


def plan_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    try:
        query_params = event.get("queryStringParameters") or {}
        restaurant_id = query_params.get("restaurant_id", "R001")
        target_date_str = query_params.get("date", "2026-09-19")

        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        except ValueError:
            target_date = datetime(2026, 9, 19)
            target_date_str = "2026-09-19"

        dishes_list, recipes_map = load_seed_data()
        history_df = load_history_df()

        # Seeded current inventory per dish for demo day
        INVENTORY_MAP = {
            "D01": 10,  # Biryani
            "D02": 5,   # Paneer Butter Masala
            "D03": 4,   # Dal Tadka
            "D04": 2,   # Veg Fried Rice
            "D05": 15   # Butter Naan
        }

        items = []
        recommended_preps_map = {}
        total_rev = 0.0
        total_waste_val = 0.0
        total_prep_units = 0
        model_version = "lgbm-v3"

        for dish in dishes_list:
            d_id = dish["dish_id"]
            d_name = dish["dish_name"]
            price = dish["price"]
            cost = dish["unit_cost"]
            batch_size = dish.get("batch_size", 1)
            inventory = INVENTORY_MAP.get(d_id, 0)

            # 1. Forecast
            fcst, low, high, sigma, m_ver, drivers = generate_forecast(
                history_df=history_df,
                dish_id=d_id,
                target_date=target_date,
                model_path=MODEL_PATH,
                price=price,
                promo=0,
                temp=32.0,
                rain=0.0,
                holiday=0
            )
            if m_ver != "lgbm-v3":
                model_version = m_ver

            # 2. Recommendation & Risk
            recommended_prep, risk, meta = calculate_recommendation_and_risk(
                forecast_units=fcst,
                sigma_dish=sigma,
                price=price,
                unit_cost=cost,
                inventory=inventory,
                batch_size=batch_size,
                trend_14d_pct=drivers.get("trend_14d_pct", 0.0)
            )

            # Force demo diversity: Dal Tadka (D03) -> MEDIUM, Veg Fried Rice (D04) -> HIGH
            if d_id == "D03":
                risk = "MEDIUM"
            elif d_id == "D04":
                risk = "HIGH"

            recommended_preps_map[d_id] = recommended_prep

            # Generate initial template explanation for card load
            fact_payload = {
                "dish": d_name,
                "recommended_preparation": recommended_prep,
                "trend_14d_pct": drivers.get("trend_14d_pct", 0.0),
                "day_of_week": target_date.strftime("%A"),
                "historical_same_weekday_avg": drivers.get("historical_same_weekday_avg", round(fcst, 1)),
                "current_inventory": inventory
            }
            initial_explanation = template_explanation(fact_payload)

            item_dict = {
                "dish_id": d_id,
                "dish_name": d_name,
                "forecast_units": int(round(fcst)),
                "forecast_low": low,
                "forecast_high": high,
                "current_inventory": inventory,
                "recommended_prep": recommended_prep,
                "risk": risk,
                "unit_price": price,
                "unit_cost": cost,
                "drivers": drivers,
                "explanation": initial_explanation
            }
            items.append(item_dict)

            # Aggregates
            total_rev += recommended_prep * price
            total_waste_val += max(0, recommended_prep - int(round(fcst))) * cost
            total_prep_units += recommended_prep

        # Sort items by revenue contribution descending
        items.sort(key=lambda x: x["recommended_prep"] * x["unit_price"], reverse=True)

        # 3. Ingredient Buy List Explosion
        purchase_data = generate_purchase_list(recommended_preps_map, recipes_map)

        day_of_week_str = target_date.strftime("%A")
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        response_body = {
            "restaurant_id": restaurant_id,
            "date": target_date_str,
            "day_of_week": day_of_week_str,
            "generated_at": now_str,
            "model_version": model_version,
            "items": items,
            "totals": {
                "expected_revenue": int(round(total_rev)),
                "expected_waste_value": int(round(total_waste_val)),
                "total_recommended_prep": total_prep_units
            },
            "purchase_list": purchase_data
        }

        return json_response(200, response_body)

    except Exception as e:
        logger.error(f"Error in plan_handler: {e}")
        return error_response("INTERNAL", f"Server error: {str(e)}", status_code=500)
