import pandas as pd
import os
import joblib
import base64
from io import BytesIO
from flask import Flask, request, render_template, redirect, url_for, send_file

from model_training.preprocessing import preprocess_input
from visualization.charts import bar_chart_top_materials, scatter_cost_vs_thermal
from visualization.multi_material_chart import multi_material_comparison_chart
from visualization.pdf_export import export_recommendations_pdf
from model_training.glass_recommendation import get_top_glass_materials

app = Flask(__name__)

# -----------------------------
# Load preprocessor and models
# -----------------------------
preprocessor = joblib.load('models_pkl/preprocessor.pkl')
suitability_model = joblib.load('models_pkl/best_suitability_model.pkl')
thermal_model = joblib.load('models_pkl/best_thermal_model.pkl')
cost_model = joblib.load('models_pkl/best_cost_model.pkl')

# Load material database
material_db = pd.read_csv('dataset/facade_material_dataset.csv')

NUMERIC_KEYS = [
    'floor_count', 'facade_area_sqm', 'max_cost_per_sqm',
    'required_u_value', 'required_shgc', 'required_vlt',
    'avg_temp_c', 'avg_humidity_pct', 'avg_rainfall_mm'
]

MATERIAL_FEATURES = [
    'material_id', 'material_type', 'material_subtype', 'cost_per_sqm',
    'installation_cost_per_sqm', 'material_u_value', 'material_shgc',
    'material_vlt_percent', 'fire_rating', 'durability_years',
    'maintenance_freq_per_year', 'acoustic_rating_rw', 'water_absorption_pct',
    'material_density_kgm3', 'surface_reflectivity_pct', 'material_lifespan_years'
]

# -----------------------------
# INDEX ROUTE
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_data = {key: request.form.get(key) for key in request.form}

        # Convert numeric inputs
        for key in NUMERIC_KEYS:
            if input_data.get(key):
                try:
                    input_data[key] = float(input_data[key])
                except ValueError:
                    input_data[key] = 0.0

        # Convert string/categorical inputs to lowercase
        for key, value in input_data.items():
            if key not in NUMERIC_KEYS and isinstance(value, str):
                input_data[key] = value.lower()

        return redirect(url_for('recommendation', **input_data))
    return render_template('index.html')


# -----------------------------
# RECOMMENDATION ROUTE
# -----------------------------
@app.route('/recommendation')
def recommendation():
    input_data = request.args.to_dict()

    # Convert numeric inputs
    for key in NUMERIC_KEYS:
        if input_data.get(key):
            input_data[key] = float(input_data[key])

    # Convert all string inputs to lowercase
    for key, value in input_data.items():
        if key not in NUMERIC_KEYS and isinstance(value, str):
            input_data[key] = value.lower()

    # -----------------------------
    # Phase-2: Material Comparison
    # -----------------------------
    preds = []
    for _, material_row in material_db.iterrows():
        combined_row = input_data.copy()
        for feature in MATERIAL_FEATURES:
            combined_row[feature] = material_row[feature]

        df_row = pd.DataFrame([combined_row])
        X_proc = preprocess_input(df_row, preprocessor)

        preds.append({
            'material_id': material_row['material_id'],
            'material_type': material_row['material_type'],
            'score': float(suitability_model.predict(X_proc)[0]),
            'thermal': float(thermal_model.predict(X_proc)[0]),
            'cost': float(cost_model.predict(X_proc)[0])
        })

    # -----------------------------
    # Top 3 unique materials by score
    # -----------------------------
    preds_sorted = sorted(preds, key=lambda x: x['score'], reverse=True)
    top_materials = []
    seen_types = set()
    for p in preds_sorted:
        if p['material_type'].lower() not in seen_types:
            top_materials.append(p)
            seen_types.add(p['material_type'].lower())
        if len(top_materials) == 3:
            break

    # -----------------------------
    # Budget warning
    # -----------------------------
    budget_warning = False
    max_budget = float(input_data.get("max_cost_per_sqm", 0))
    for mat in top_materials:
        if mat['cost'] > max_budget:
            budget_warning = True
            break

    # -----------------------------
    # Visual indicators for thermal & cost
    # -----------------------------
    THERMAL_GOOD = 0.5       # U-value threshold for green
    COST_GOOD_RATIO = 0.8    # Cost <= 80% of budget → green

    for mat in top_materials:
        mat['thermal_indicator'] = 'green' if mat['thermal'] <= THERMAL_GOOD else 'red'
        mat['cost_indicator'] = 'green' if mat['cost'] <= max_budget * COST_GOOD_RATIO else 'red'

    suitability_score = round(top_materials[0]['score'], 2)
    thermal_perf = round(top_materials[0]['thermal'], 2)
    cost_est = round(top_materials[0]['cost'], 2)

    # -----------------------------
    # Phase-1: Glass Detailed Recommendation
    # -----------------------------
    glass_df = get_top_glass_materials(top_n=5)

    # Keep top unique glass options by material_name
    glass_df = glass_df.sort_values('final_score', ascending=False)
    glass_df = glass_df.drop_duplicates(subset='material_name', keep='first')

    glass_df['score'] = glass_df['final_score']

    numeric_cols = [
        'score', 'material_u_value', 'material_shgc', 'material_vlt_percent',
        'acoustic_rating_rw', 'cost_per_sqm', 'thickness_mm'
    ]
    for col in numeric_cols:
        if col in glass_df.columns:
            glass_df[col] = glass_df[col].fillna(0)

    glass_recommendations = glass_df.to_dict(orient='records')

    # -----------------------------
    # Charts
    # -----------------------------
    chart_bar_buf = bar_chart_top_materials(top_materials)
    chart_scatter_buf = scatter_cost_vs_thermal(preds)
    chart_multi_buf = multi_material_comparison_chart(top_materials)

    chart_bar = base64.b64encode(chart_bar_buf.getvalue()).decode('utf-8')
    chart_scatter = base64.b64encode(chart_scatter_buf.getvalue()).decode('utf-8')
    chart_multi = base64.b64encode(chart_multi_buf.getvalue()).decode('utf-8')

    # -----------------------------
    # Export PDF
    # -----------------------------
    pdf_path = 'static/recommendation.pdf'
    export_recommendations_pdf(
        top_materials=top_materials,
        suitability_score=suitability_score,
        thermal_perf=thermal_perf,
        cost_est=cost_est,
        glass_recommendations=glass_recommendations,
        chart_img=chart_multi_buf,
        output_path=pdf_path
    )

    return render_template(
        'recommendation.html',
        top_materials=top_materials,
        suitability_score=suitability_score,
        thermal_perf=thermal_perf,
        cost_est=cost_est,
        chart_bar=chart_bar,
        chart_scatter=chart_scatter,
        chart_multi=chart_multi,
        pdf_file_path=pdf_path,
        glass_recommendations=glass_recommendations,
        budget_warning=budget_warning
    )


# -----------------------------
# DOWNLOAD PDF
# -----------------------------
@app.route('/download_pdf')
def download_pdf():
    pdf_path = 'static/recommendation.pdf'
    if not os.path.exists(pdf_path):
        return "PDF not found", 404
    return send_file(pdf_path, as_attachment=True)


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
