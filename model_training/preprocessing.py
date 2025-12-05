import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
import joblib

def load_dataset(path="dataset/facade_material_dataset.csv"):
    df = pd.read_csv(path)
    return df

def fit_preprocessor(df):
    categorical_features = [
        'location', 'building_type', 'orientation', 'acoustic_requirement',
        'fire_rating_requirement', 'aesthetic_preference',
        'thermal_insulation_required', 'wind_load_level', 'climate_zone', 'solar_exposure'
    ]
    numeric_features = [
        'floor_count', 'facade_area_sqm', 'max_cost_per_sqm',
        'required_u_value', 'required_shgc', 'required_vlt',
        'avg_temp_c', 'avg_humidity_pct', 'avg_rainfall_mm'
    ]
    ordinal_features = ['budget_level']
    budget_level_order = ['low', 'medium', 'high']

    preprocessor = ColumnTransformer(
        transformers=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'), 
             [f for f in categorical_features if f not in ordinal_features]),
            ('ordinal', OrdinalEncoder(categories=[budget_level_order]), ordinal_features),
            ('scale', StandardScaler(), numeric_features)
        ],
        remainder='drop'
    )
    preprocessor.fit(df[categorical_features + ordinal_features + numeric_features])
    joblib.dump(preprocessor, 'models_pkl/preprocessor.pkl')
    print("Preprocessor fitted and saved as 'preprocessor.pkl'")
    return preprocessor

def preprocess_input(df, preprocessor):
    features_order = [
        'location', 'building_type', 'orientation', 'acoustic_requirement',
        'fire_rating_requirement', 'aesthetic_preference',
        'thermal_insulation_required', 'wind_load_level', 'climate_zone', 'solar_exposure',
        'budget_level',
        'floor_count', 'facade_area_sqm', 'max_cost_per_sqm',
        'required_u_value', 'required_shgc', 'required_vlt',
        'avg_temp_c', 'avg_humidity_pct', 'avg_rainfall_mm'
    ]
    df = df[features_order]
    X = preprocessor.transform(df)
    return X
