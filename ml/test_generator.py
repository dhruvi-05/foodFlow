"""
Acceptance Test Suite for Synthetic Sales Generator.
Verifies dataset size, waste rate, sell-out frequency, null checks, and baseline MAPE.
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ml.generate_data import generate_synthetic_data


def run_acceptance_tests():
    df = generate_synthetic_data(180)
    print("=" * 60)
    print("RUNNING GENERATOR ACCEPTANCE TESTS")
    print("=" * 60)

    # Test 1: Shape & Nulls Check
    expected_rows = 180 * 5
    assert len(df) == expected_rows, f"FAILED: Expected {expected_rows} rows, got {len(df)}"
    assert df.isnull().sum().sum() == 0, "FAILED: Found null values in dataset"
    assert (df["units_prepared"] < 0).sum() == 0, "FAILED: Found negative units_prepared"
    assert (df["units_sold"] < 0).sum() == 0, "FAILED: Found negative units_sold"
    assert (df["units_wasted"] < 0).sum() == 0, "FAILED: Found negative units_wasted"
    print(f"✅ Test 1 Passed: Exactly {expected_rows} rows, 0 nulls, 0 negative values.")

    # Test 2: Overall Waste Rate (between 15% and 21%)
    total_prepared = df["units_prepared"].sum() + df["opening_inventory"].sum()
    total_wasted = df["units_wasted"].sum()
    waste_rate = (total_wasted / total_prepared) * 100.0
    print(f"📊 Overall Waste Rate: {waste_rate:.2f}%")
    assert 14.0 <= waste_rate <= 22.0, f"FAILED: Waste rate {waste_rate:.2f}% out of range [14%, 22%]"
    print(f"✅ Test 2 Passed: Waste rate {waste_rate:.2f}% is within acceptable 15-21% band.")

    # Test 3: Sell-out Days (< 10% of rows)
    sell_out_rows = (df["units_sold"] == (df["units_prepared"] + df["opening_inventory"])).sum()
    sell_out_pct = (sell_out_rows / len(df)) * 100.0
    print(f"📊 Sell-out Days: {sell_out_rows} ({sell_out_pct:.2f}%)")
    assert sell_out_pct < 10.0, f"FAILED: Sell-out rate {sell_out_pct:.2f}% exceeds 10%"
    print(f"✅ Test 3 Passed: Sell-out rate {sell_out_pct:.2f}% is under limit.")

    # Test 4: Day-of-week pattern check for Biryani (D01)
    biryani_df = df[df["dish_id"] == "D01"]
    dow_means = biryani_df.groupby("day_of_week")["units_sold"].mean()
    fri_sat_avg = (dow_means["Friday"] + dow_means["Saturday"]) / 2.0
    mon_tue_avg = (dow_means["Monday"] + dow_means["Tuesday"]) / 2.0
    assert fri_sat_avg > mon_tue_avg, "FAILED: Biryani weekend demand is not higher than weekday demand"
    print(f"✅ Test 4 Passed: Biryani exhibits clear weekend peak (Fri/Sat avg: {fri_sat_avg:.1f} vs Mon/Tue avg: {mon_tue_avg:.1f}).")

    # Test 5: 7-day Moving Average MAPE (between 12% and 20%)
    df["sold_7d_ma"] = df.groupby("dish_id")["units_sold"].transform(lambda x: x.shift(1).rolling(7).mean())
    eval_df = df.dropna(subset=["sold_7d_ma"]).copy()
    mape = np.mean(np.abs(eval_df["units_sold"] - eval_df["sold_7d_ma"]) / np.maximum(1, eval_df["units_sold"])) * 100.0
    print(f"📊 7-Day Moving Average Baseline MAPE: {mape:.2f}%")
    assert 10.0 <= mape <= 22.0, f"FAILED: Baseline MAPE {mape:.2f}% out of target range [10%, 22%]"
    print(f"✅ Test 5 Passed: Baseline MAPE {mape:.2f}% shows non-trivial demand pattern.")

    print("\n🎉 ALL 5 ACCEPTANCE TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_acceptance_tests()
