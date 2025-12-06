import os
import pandas as pd
import joblib
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Ensure models directory exists
os.makedirs("models_pkl", exist_ok=True)


# -----------------------------
# LOAD DATASET
# -----------------------------
def load_dataset(path):
    """Load dataset CSV."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}")
    df = pd.read_csv(path)
    print(f"[INFO] Dataset loaded from {path} with shape: {df.shape}")
    return df


# -----------------------------
# FIT PREPROCESSOR
# -----------------------------
def fit_preprocessor(df, phase="phase2"):
    """
    Fit and save a ColumnTransformer for preprocessing.
    phase: "phase1" = glass dataset, "phase2" = facade materials
    """

    if phase == "phase1":
        # Phase-1: glass dataset features
        categorical_features = [
            'glass_type', 'recommended_climate', 'fire_rating',
            'solar_control_coating', 'environmental_suitability'
        ]
        numeric_features = [
            'u_value', 'shgc', 'vlt', 'acoustic_rw', 'thickness_mm',
            'durability_years', 'cost_per_sqm', 'maintenance_freq_per_year',
            'impact_resistance'
        ]
        save_name = "preprocessor_phase1.pkl"

    else:
        # Phase-2: all material features
        categorical_features = [
            'location', 'building_type', 'orientation', 'budget_level',
            'acoustic_requirement', 'fire_rating_requirement',
            'aesthetic_preference', 'thermal_insulation_required',
            'wind_load_level', 'climate_zone', 'material_type',
            'material_subtype', 'fire_rating', 'solar_exposure'
        ]
        numeric_features = [
            'floor_count', 'facade_area_sqm', 'max_cost_per_sqm',
            'required_u_value', 'required_shgc', 'required_vlt',
            'avg_temp_c', 'avg_humidity_pct', 'avg_rainfall_mm',
            'cost_per_sqm', 'installation_cost_per_sqm', 'material_u_value',
            'material_shgc', 'material_vlt_percent', 'durability_years',
            'maintenance_freq_per_year', 'acoustic_rating_rw',
            'water_absorption_pct', 'material_density_kgm3',
            'surface_reflectivity_pct', 'material_lifespan_years'
        ]
        save_name = "preprocessor_phase2.pkl"

    # Fill missing values
    for col in numeric_features:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    for col in categorical_features:
        if col in df.columns:
            df[col] = df[col].fillna('unknown')
            df[col] = df[col].astype(str).str.lower()  # <-- convert categorical to lowercase

    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", StandardScaler(), numeric_features)
        ]
    )

    # Fit preprocessor
    print(f"[INFO] Fitting preprocessor for {phase}...")
    preprocessor.fit(df[categorical_features + numeric_features])

    # Save preprocessor
    save_path = f"models_pkl/{save_name}"
    joblib.dump(preprocessor, save_path)
    print(f"[INFO] Preprocessor saved at {save_path}")

    # For main.py compatibility, save a copy as 'preprocessor.pkl' for phase2
    if phase == "phase2":
        joblib.dump(preprocessor, "models_pkl/preprocessor.pkl")
        print(f"[INFO] Also saved preprocessor.pkl for main.py")

    return preprocessor


# -----------------------------
# PREPROCESS INPUT
# -----------------------------
def preprocess_input(df, preprocessor):
    """Transform input dataframe using fitted preprocessor."""
    if df.empty:
        raise ValueError("Input dataframe is empty")
    
    # Convert categorical columns in input to lowercase
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        df[col] = df[col].astype(str).str.lower()
    
    return preprocessor.transform(df)


# -----------------------------
# CLI USAGE
# -----------------------------
if __name__ == "__main__":
    # Fit both phase1 and phase2 preprocessors
    df_phase2 = load_dataset("dataset/facade_material_dataset.csv")
    fit_preprocessor(df_phase2, phase="phase2")

    df_phase1 = load_dataset("dataset/glass_dataset.csv")
    fit_preprocessor(df_phase1, phase="phase1")
