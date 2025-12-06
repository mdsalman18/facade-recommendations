import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import optuna
from numpy import sqrt
from model_training.preprocessing import load_dataset, fit_preprocessor, preprocess_input

# Ensure models directory exists
os.makedirs("models_pkl", exist_ok=True)

# -----------------------------
# MODEL FACTORY
# -----------------------------
def create_model(trial, model_name):
    if model_name == "catboost":
        return CatBoostRegressor(
            depth=trial.suggest_int("depth", 4, 10),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
            iterations=trial.suggest_int("iterations", 300, 1200),
            l2_leaf_reg=trial.suggest_float("l2_leaf_reg", 1, 10),
            verbose=0
        )

    if model_name == "xgboost":
        return XGBRegressor(
            max_depth=trial.suggest_int("max_depth", 3, 12),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
            n_estimators=trial.suggest_int("n_estimators", 300, 1200),
            subsample=trial.suggest_float("subsample", 0.5, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
            reg_lambda=trial.suggest_float("reg_lambda", 1, 15),
            objective="reg:squarederror",
            n_jobs=-1
        )

    if model_name == "lightgbm":
        return LGBMRegressor(
            num_leaves=trial.suggest_int("num_leaves", 20, 150),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
            n_estimators=trial.suggest_int("n_estimators", 300, 1200),
            subsample=trial.suggest_float("subsample", 0.6, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
            n_jobs=-1
        )

# -----------------------------
# OPTUNA TUNING
# -----------------------------
def tune_model(model_name, X_train, X_test, y_train, y_test, n_trials=15):
    def objective(trial):
        model = create_model(trial, model_name)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        rmse = sqrt(mean_squared_error(y_test, preds))
        return rmse

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    best_trial = study.best_trial
    print(f"[INFO] Best RMSE for {model_name}: {best_trial.value:.4f}")
    print(f"[INFO] Best hyperparameters for {model_name}: {best_trial.params}")

    best_model = create_model(best_trial, model_name)
    best_model.fit(X_train, y_train)

    return best_model, best_trial.value

# -----------------------------
# SELECT BEST MODEL
# -----------------------------
def get_best_model(X_train, X_test, y_train, y_test):
    model_names = ["catboost", "xgboost", "lightgbm"]

    best_score = float("inf")
    best_model = None
    best_name = None

    for name in model_names:
        print(f"\n[INFO] Tuning model: {name}")
        model, score = tune_model(name, X_train, X_test, y_train, y_test)
        if score < best_score:
            best_score = score
            best_model = model
            best_name = name

    print(f"\n[INFO] BEST MODEL SELECTED: {best_name} with RMSE = {best_score:.4f}\n")
    return best_model

# -----------------------------
# MAIN TRAINING FUNCTION
# -----------------------------
def train_all_targets():
    df = load_dataset("dataset/facade_material_dataset.csv")
    feature_cols = [col for col in df.columns if col not in ["suitability_score",
                                                             "thermal_gap_u_value",
                                                             "total_cost_estimate"]]
    targets = {
        "suitability": "suitability_score",
        "thermal": "thermal_gap_u_value",
        "cost": "total_cost_estimate"
    }

    preprocessor = fit_preprocessor(df)

    for name, target in targets.items():
        print(f"\n==============================")
        print(f"[INFO] TRAINING FOR TARGET: {name.upper()}")
        print(f"==============================\n")

        X_train, X_test, y_train, y_test = train_test_split(
            df[feature_cols], df[target], test_size=0.2, random_state=42
        )

        X_train_p = preprocess_input(X_train, preprocessor)
        X_test_p = preprocess_input(X_test, preprocessor)

        best_model = get_best_model(X_train_p, X_test_p, y_train, y_test)
        joblib.dump(best_model, f"models_pkl/best_{name}_model.pkl")
        print(f"[INFO] Saved → models_pkl/best_{name}_model.pkl")

    print("\n[INFO] 🎉 All models trained successfully!")

if __name__ == "__main__":
    train_all_targets()
