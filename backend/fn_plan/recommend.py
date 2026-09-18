"""
Newsvendor Recommendation & Risk Banding Engine for WasteWise AI.
Calculates margin-aware prep quantities and assigns risk levels (LOW, MEDIUM, HIGH).
"""

import math
from typing import Tuple, Dict, Any
from backend.fn_plan.forecast import get_z_score


def calculate_recommendation_and_risk(
    forecast_units: float,
    sigma_dish: float,
    price: float,
    unit_cost: float,
    inventory: int,
    batch_size: int = 1,
    trend_14d_pct: float = 0.0,
    same_dow_obs_count: int = 4
) -> Tuple[int, str, Dict[str, Any]]:
    """
    Computes optimal prep quantity using Newsvendor critical ratio + batching,
    and assigns risk band (LOW | MEDIUM | HIGH).
    """
    cu = max(1.0, price - unit_cost)  # Cost of under-preparing (lost margin)
    co = max(1.0, unit_cost)          # Cost of over-preparing (wasted food cost)
    critical_ratio = cu / (cu + co)

    z = get_z_score(critical_ratio)
    raw_safety_buffer = z * sigma_dish
    
    # Cap safety buffer at 15% of forecast
    max_buffer = 0.15 * forecast_units
    safety_buffer = min(raw_safety_buffer, max_buffer)

    usable_inventory = float(inventory)
    raw_prep = forecast_units + safety_buffer - usable_inventory
    raw_prep_clamped = max(0.0, raw_prep)

    # Batching to kitchen units
    if batch_size > 1:
        recommended_prep = int(math.ceil(raw_prep_clamped / float(batch_size)) * batch_size)
    else:
        recommended_prep = int(round(raw_prep_clamped))

    # Coefficient of Variation
    cv = sigma_dish / max(1.0, forecast_units)
    inv_cover_pct = (usable_inventory / max(1.0, forecast_units)) * 100.0

    # Risk Banding Logic (Section 8.2)
    if cv >= 0.28 or inv_cover_pct > 50.0 or same_dow_obs_count < 3:
        risk = "HIGH"
    elif (0.15 <= cv < 0.28) or (trend_14d_pct < -8.0):
        risk = "MEDIUM"
    else:
        risk = "LOW"

    meta = {
        "critical_ratio": round(critical_ratio, 3),
        "z_score": round(z, 2),
        "safety_buffer": round(safety_buffer, 1),
        "cv": round(cv, 3),
        "inv_cover_pct": round(inv_cover_pct, 1)
    }

    return recommended_prep, risk, meta
