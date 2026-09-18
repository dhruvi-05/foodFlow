"""
LightGBM Model Training Script for WasteWise AI.
Trains a single global LightGBM model across all 5 dishes using time-based validation.
"""

import os
import sys
import numpy as np
import pandas as pd
import lightgbm as lgb
from datetime import datetime

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def build_training_features(df: pd.DataFrame) -> pd.DataFrame:
    """Builds lag, rolling, calendar, and weather features for training."""
    df = df.sort_values(["dish_id", "date"]).reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    
    start_date = df["date"].min()
    df["days_since_start"] = (df["date"] - start_date).dt.days
    df["month"] = df["date"].dt.month
    df["day_of_month"] = df["date"].dt.day
    df["day_of_week_num"] = df["date"].dt.weekday
    df["is_weekend"] = df["day_of_week_num"].apply(lambda x: 1 if x in [4, 5, 6] else 0)

    # Grouped lag features
    for lag in [1, 2, 7, 14, 21, 28]:
        df[f"lag_{lag}"] = df.groupby("dish_id")["units_sold"].shift(lag)

    # Grouped rolling features
    df["roll_mean_7"] = df.groupby("dish_id")["units_sold"].transform(lambda x: x.shift(1).rolling(7).mean())
    df["roll_mean_14"] = df.groupby("dish_id")["units_sold"].transform(lambda x: x.shift(1).rolling(14).mean())
    df["roll_std_7"] = df.groupby("dish_id")["units_sold"].transform(lambda x: x.shift(1).rolling(7).std())
    df["roll_max_7"] = df.groupby("dish_id")["units_sold"].transform(lambda x: x.shift(1).rolling(7).max())

    # Same weekday rolling mean
    df["roll_mean_same_dow_4"] = df.groupby(["dish_id", "day_of_week_num"])["units_sold"].transform(lambda x: x.shift(1).rolling(4).mean())

    # Ratio features
    df["lag_1_div_roll7"] = df["lag_1"] / np.maximum(1.0, df["roll_mean_7"])
    df["roll7_div_roll14"] = df["roll_mean_7"] / np.maximum(1.0, df["roll_mean_14"])

    # Commercial & External
    df["price_vs_30d_mean"] = 1.0
    df["rain_flag"] = (df["rainfall"] > 5.0).astype(int)

    # Fill NaNs from shift operations
    df = df.dropna().reset_index(drop=True)
    return df


def train_model():
    data_path = os.path.join(os.path.dirname(__file__), "data", "sales_history.csv")
    if not os.path.exists(data_path):
        from ml.generate_data import generate_synthetic_data
        df_raw = generate_synthetic_data(180)
        df_raw.to_csv(data_path, index=False)
    else:
        df_raw = pd.read_csv(data_path)

    df_featured = build_training_features(df_raw)

    # Time-based split: hold out last 30 days for validation
    max_date = df_featured["date"].max()
    cutoff_date = max_date - pd.Timedelta(days=30)
    
    train_df = df_featured[df_featured["date"] < cutoff_date].copy()
    valid_df = df_featured[df_featured["date"] >= cutoff_date].copy()

    feature_cols = [
        "dish_id", "day_of_week_num", "is_weekend", "month", "day_of_month",
        "holiday", "days_since_start", "lag_1", "lag_2", "lag_7", "lag_14",
        "lag_21", "lag_28", "roll_mean_7", "roll_mean_14", "roll_std_7",
        "roll_max_7", "roll_mean_same_dow_4", "lag_1_div_roll7",
        "roll7_div_roll14", "price", "promotion", "price_vs_30d_mean",
        "temperature", "rainfall", "rain_flag"
    ]

    # Convert categoricals
    for col in ["dish_id", "day_of_week_num"]:
        train_df[col] = train_df[col].astype("category")
        valid_df[col] = valid_df[col].astype("category")

    X_train, y_train = train_df[feature_cols], train_df["units_sold"]
    X_valid, y_valid = valid_df[feature_cols], valid_df["units_sold"]

    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_valid, label=y_valid, reference=train_data)

    params = {
        "objective": "regression_l1",
        "metric": "mae",
        "learning_rate": 0.05,
        "num_leaves": 15,
        "min_data_in_leaf": 20,
        "feature_fraction": 0.85,
        "bagging_fraction": 0.85,
        "bagging_freq": 1,
        "lambda_l2": 1.0,
        "verbosity": -1,
        "random_state": 42
    }

    booster = lgb.train(
        params,
        train_data,
        num_boost_round=800,
        valid_sets=[valid_data],
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )

    preds = booster.predict(X_valid)
    mae = float(np.mean(np.abs(preds - y_valid)))
    mape = float(np.mean(np.abs(preds - y_valid) / np.maximum(1, y_valid))) * 100.0

    print("=" * 60)
    print(f"LIGHTGBM TRAINING COMPLETE")
    print(f"Validation MAE  : {mae:.2f} units")
    print(f"Validation MAPE : {mape:.2f}%")
    print("=" * 60)

    # Save model artifacts
    out_models_dir = os.path.join(os.path.dirname(__file__), "..", "models", "lgbm-v3")
    os.makedirs(out_models_dir, exist_ok=True)
    model_txt = os.path.join(out_models_dir, "model.txt")
    booster.save_model(model_txt)

    fn_plan_model = os.path.join(os.path.dirname(__file__), "..", "backend", "fn_plan", "model.txt")
    os.makedirs(os.path.dirname(fn_plan_model), exist_ok=True)
    booster.save_model(fn_plan_model)

    print(f"Saved model booster to {model_txt} and {fn_plan_model}")
    return mae, mape


if __name__ == "__main__":
    train_model()
