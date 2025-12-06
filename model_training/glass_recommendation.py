# glass_recommendation.py
import pandas as pd
import os

GLASS_DATASET_PATH = "dataset/glass_dataset.csv"

def get_top_glass_materials(input_data=None, top_n=5):
    """
    Return top N glass materials for the customer, considering duplicates
    and input constraints.
    
    input_data: dict containing customer's requirements
    """
    if not os.path.exists(GLASS_DATASET_PATH):
        raise FileNotFoundError(f"Glass dataset not found at {GLASS_DATASET_PATH}")

    df = pd.read_csv(GLASS_DATASET_PATH)

    required_cols = [
        "glass_type", "u_value", "shgc", "vlt",
        "acoustic_rw", "thickness_mm", "fire_rating",
        "durability_years", "cost_per_sqm",
        "maintenance_freq_per_year", "solar_control_coating",
        "impact_resistance", "environmental_suitability"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert numeric columns to float
    numeric_cols = ["u_value", "shgc", "vlt", "durability_years", "acoustic_rw", "cost_per_sqm", "thickness_mm", "maintenance_freq_per_year"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Weighted score
    df["thermal_score"] = 100 - (df["u_value"] * 20)
    df["solar_score"] = 100 - (df["shgc"] * 100)
    df["clarity_score"] = df["vlt"]
    df["durability_score"] = df["durability_years"] * 5
    df["acoustic_score"] = df["acoustic_rw"] * 5
    df["cost_score"] = 100 - (df["cost_per_sqm"] / df["cost_per_sqm"].max() * 100)

    df["final_score"] = (
        df["thermal_score"] * 0.25 +
        df["solar_score"] * 0.20 +
        df["clarity_score"] * 0.20 +
        df["durability_score"] * 0.15 +
        df["acoustic_score"] * 0.10 +
        df["cost_score"] * 0.10
    )

    # Apply customer constraints if input_data is provided
    if input_data:
        # Filter by max cost
        if "max_cost_per_sqm" in input_data:
            df = df[df["cost_per_sqm"] <= float(input_data["max_cost_per_sqm"])]
        # Filter by U-Value
        if "required_u_value" in input_data:
            df = df[df["u_value"] <= float(input_data["required_u_value"])]
        # Filter by SHGC
        if "required_shgc" in input_data:
            df = df[df["shgc"] <= float(input_data["required_shgc"])]
        # Filter by VLT
        if "required_vlt" in input_data:
            df = df[df["vlt"] >= float(input_data["required_vlt"])]
        # Filter by acoustic requirement
        if "acoustic_requirement" in input_data and input_data["acoustic_requirement"].lower() == "yes":
            df = df[df["acoustic_rw"] >= 40]  # Example threshold

    # Sort by final score descending
    df_sorted = df.sort_values(by="final_score", ascending=False)

    # Remove duplicates: keep the highest scoring option per glass_type
    df_unique = df_sorted.drop_duplicates(subset="glass_type", keep="first")

    # Rename for template consistency
    df_unique = df_unique.rename(columns={
        "glass_type": "material_name",
        "vlt": "material_vlt_percent",
        "u_value": "material_u_value",
        "shgc": "material_shgc",
        "acoustic_rw": "acoustic_rating_rw"
    })

    # Return top N
    return df_unique.head(top_n)
