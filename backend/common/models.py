"""
Data models and dataclasses for WasteWise AI.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any


@dataclass
class SalesRow:
    date: str  # ISO YYYY-MM-DD
    restaurant_id: str
    dish_id: str
    dish_name: str
    category: str
    price: float
    promotion: int  # 0 or 1
    day_of_week: str  # Monday..Sunday
    holiday: int  # 0 or 1
    temperature: float
    rainfall: float
    units_prepared: int
    units_sold: int
    units_wasted: int
    waste_reason: str  # overproduction | expiry | prep_error | other
    opening_inventory: int = 0
    closing_inventory: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Drivers:
    friday_uplift_pct: float = 0.0
    last_3_friday_avg: float = 0.0
    trend_7d_pct: float = 0.0
    trend_14d_pct: float = 0.0
    rain_flag: bool = False
    historical_same_weekday_avg: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanItem:
    dish_id: str
    dish_name: str
    forecast_units: int
    forecast_low: int
    forecast_high: int
    current_inventory: int
    recommended_prep: int
    risk: str  # LOW | MEDIUM | HIGH
    unit_price: float
    unit_cost: float
    drivers: Dict[str, Any] = field(default_factory=dict)
    explanation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IngredientPurchaseItem:
    ingredient: str
    required_kg: float
    in_stock_kg: float
    buy_kg: float
    rounded_buy_kg: float
    est_cost: float
    urgent: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PurchaseListResponse:
    purchase_list: List[Dict[str, Any]]
    total_est_cost: float
    lines_sufficient: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanTotals:
    expected_revenue: float
    expected_waste_value: float
    total_recommended_prep: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanResponse:
    restaurant_id: str
    date: str
    day_of_week: str
    generated_at: str
    model_version: str
    items: List[Dict[str, Any]]
    totals: Dict[str, Any]
    purchase_list: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
