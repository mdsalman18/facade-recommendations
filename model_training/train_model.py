import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor

from model_training.preprocessing import load_dataset, fit_preprocessor, preprocess_input

def train_models():
    df = load_dataset()

    # Fit preprocessor
    preprocessor = fit_preprocessor(df)

    # Features for model
    feature_cols = [
        'location', 'building_type', 'orientation', 'acoustic_requirement',
        'fire_rating_requirement', 'aesthetic_preference',
        'thermal_insulation_required', 'wind_load_level', 'climate_zone', 'solar_exposure',
        'budget_level',
        'floor_count', 'facade_area_sqm', 'max_cost_per_sqm',
        'required_u_value', 'required_shgc', 'required_vlt',
        'avg_temp_c', 'avg_humidity_pct', 'avg_rainfall_mm'
    ]

    # Targets
    y_suitability = df['suitability_score']
    y_thermal = df['thermal_gap_u_value']  # or any column for thermal performance
    y_cost = df['total_cost_estimate']

    X_train, X_test, y_train_s, y_test_s = train_test_split(df[feature_cols], y_suitability, test_size=0.2, random_state=42)
    _, _, y_train_t, y_test_t = train_test_split(df[feature_cols], y_thermal, test_size=0.2, random_state=42)
    _, _, y_train_c, y_test_c = train_test_split(df[feature_cols], y_cost, test_size=0.2, random_state=42)

    # Preprocess
    X_train_proc = preprocess_input(X_train, preprocessor)
    X_test_proc = preprocess_input(X_test, preprocessor)

    # Train models
    clf_model = CatBoostRegressor(verbose=0, random_state=42)
    clf_model.fit(X_train_proc, y_train_s)

    thermal_model = CatBoostRegressor(verbose=0, random_state=42)
    thermal_model.fit(X_train_proc, y_train_t)

    cost_model = CatBoostRegressor(verbose=0, random_state=42)
    cost_model.fit(X_train_proc, y_train_c)

    # Save models
    joblib.dump(clf_model, 'models_pkl/suitability_model.pkl')
    joblib.dump(thermal_model, 'models_pkl/thermal_model.pkl')
    joblib.dump(cost_model, 'models_pkl/cost_model.pkl')
    print("All models saved in models_pkl folder.")

if __name__ == "__main__":
    train_models()
