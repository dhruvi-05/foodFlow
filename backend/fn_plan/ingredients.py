"""
Recipe Explosion and Purchase List Generator for WasteWise AI.
Converts recommended dish prep quantities into ingredient purchase requirements in kg.
"""

import json
import math
from typing import Dict, List, Any


def generate_purchase_list(
    recommended_preps: Dict[str, int],
    recipes_map: Dict[str, Dict[str, Any]],
    current_inventory_kg: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Explodes dish prep quantities into ingredient demand in kg, applies yield loss,
    subtracts in-stock inventory, and rounds to supplier purchase increments.
    """
    if current_inventory_kg is None:
        current_inventory_kg = {
            "rice": 5.20,
            "chicken": 3.10,
            "onion": 1.50,
            "tomato": 0.80,
            "spices": 0.20,
            "paneer": 2.00,
            "butter": 0.50,
            "cream": 0.30,
            "dal": 3.00,
            "ghee": 0.80,
            "maida": 4.00,
            "milk": 1.00,
            "mixed_veggies": 2.00,
            "oil": 2.50,
            "soy_sauce": 0.50,
            "yeast_sugar": 0.10
        }

    raw_req_grams: Dict[str, float] = {}
    ingredient_meta: Dict[str, Dict[str, Any]] = {}

    # Step 1 & 2: Multiply prep quantity by grams and sum across dishes
    for dish_id, prep_qty in recommended_preps.items():
        if prep_qty <= 0 or dish_id not in recipes_map:
            continue
        
        recipe = recipes_map[dish_id]
        for ing_name, ing_info in recipe.items():
            grams = ing_info["grams"] * prep_qty
            raw_req_grams[ing_name] = raw_req_grams.get(ing_name, 0.0) + grams
            if ing_name not in ingredient_meta:
                ingredient_meta[ing_name] = {
                    "cost_per_kg": ing_info.get("cost_per_kg", 100.0),
                    "yield_factor": ing_info.get("yield_factor", 1.0),
                    "buy_increment_kg": ing_info.get("buy_increment_kg", 1.0)
                }

    items = []
    total_est_cost = 0.0
    sufficient_count = 0

    # Step 3, 4, 5, 6: Yield loss, inventory subtraction, rounding
    for ing_name, grams in raw_req_grams.items():
        meta = ingredient_meta[ing_name]
        yield_factor = meta["yield_factor"]
        cost_per_kg = meta["cost_per_kg"]
        buy_inc = meta["buy_increment_kg"]

        # Gross requirement accounting for peeling/trimming loss
        gross_req_kg = round((grams / 1000.0) / yield_factor, 2)
        in_stock = current_inventory_kg.get(ing_name, 0.0)
        net_buy_kg = max(0.0, gross_req_kg - in_stock)

        # Round up to purchase increment
        if net_buy_kg > 0:
            rounded_buy_kg = round(math.ceil(net_buy_kg / buy_inc) * buy_inc, 2)
        else:
            rounded_buy_kg = 0.0

        est_cost = round(rounded_buy_kg * cost_per_kg, 2)
        total_est_cost += est_cost

        is_urgent = (gross_req_kg > 0) and ((gross_req_kg - in_stock) / gross_req_kg > 0.50)
        
        if in_stock >= gross_req_kg:
            sufficient_count += 1

        items.append({
            "ingredient": ing_name.replace("_", " ").title(),
            "required_kg": gross_req_kg,
            "in_stock_kg": round(in_stock, 2),
            "buy_kg": round(net_buy_kg, 2),
            "rounded_buy_kg": rounded_buy_kg,
            "est_cost": int(est_cost),
            "urgent": is_urgent
        })

    # Sort urgent items first, then by estimated cost descending
    items.sort(key=lambda x: (not x["urgent"], -x["est_cost"]))

    return {
        "purchase_list": items,
        "total_est_cost": int(round(total_est_cost)),
        "lines_sufficient": sufficient_count
    }
