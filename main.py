from flask import Flask, request, render_template, redirect, url_for, send_file
import pandas as pd
import joblib
import io
import base64
import os

from model_training.preprocessing import preprocess_input
from visualization.charts import bar_chart_top_materials, scatter_cost_vs_thermal
from visualization.multi_material_chart import multi_material_comparison_chart
from visualization.pdf_export import export_recommendations_pdf

app = Flask(__name__)

# Load preprocessor and models
preprocessor = joblib.load('models_pkl/preprocessor.pkl')
suitability_model = joblib.load('models_pkl/suitability_model.pkl')
thermal_model = joblib.load('models_pkl/thermal_model.pkl')
cost_model = joblib.load('models_pkl/cost_model.pkl')

# Load material database
material_db = pd.read_csv('dataset/facade_material_dataset.csv')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Homepage with form, redirects to /recommendation on submit"""
    if request.method == 'POST':
        # Collect input
        input_data = {key: request.form.get(key) for key in request.form}

        # Convert numeric fields to float
        numeric_keys = [
            'floor_count', 'facade_area_sqm', 'max_cost_per_sqm',
            'required_u_value', 'required_shgc', 'required_vlt',
            'avg_temp_c', 'avg_humidity_pct', 'avg_rainfall_mm'
        ]
        for key in numeric_keys:
            if key in input_data and input_data[key]:
                input_data[key] = float(input_data[key])

        # Redirect to recommendation page passing input as query parameters
        return redirect(url_for('recommendation', **input_data))

    return render_template('index.html')


@app.route('/recommendation')
def recommendation():
    """Compute predictions and render recommendation page"""
    # Get input data from query params
    input_data = request.args.to_dict()

    numeric_keys = [
        'floor_count', 'facade_area_sqm', 'max_cost_per_sqm',
        'required_u_value', 'required_shgc', 'required_vlt',
        'avg_temp_c', 'avg_humidity_pct', 'avg_rainfall_mm'
    ]
    for key in numeric_keys:
        input_data[key] = float(input_data[key])

    # Predict for all materials
    preds = []
    for _, material_row in material_db.iterrows():
        df_row = pd.DataFrame([input_data])
        X_proc = preprocess_input(df_row, preprocessor)
        preds.append({
            'material_id': material_row['material_id'],
            'material_type': material_row['material_type'],
            'score': float(suitability_model.predict(X_proc)[0]),
            'thermal': float(thermal_model.predict(X_proc)[0]),
            'cost': float(cost_model.predict(X_proc)[0])
        })

    # Select top 3 unique materials
    preds_sorted = sorted(preds, key=lambda x: x['score'], reverse=True)
    top_materials = []
    seen_types = set()
    for p in preds_sorted:
        if p['material_type'] not in seen_types:
            top_materials.append(p)
            seen_types.add(p['material_type'])
        if len(top_materials) == 3:
            break

    # Summary values
    suitability_score = round(top_materials[0]['score'], 2)
    thermal_perf = round(top_materials[0]['thermal'], 2)
    cost_est = round(top_materials[0]['cost'], 2)

    # Charts
    chart_bar = bar_chart_top_materials(top_materials)
    chart_scatter = scatter_cost_vs_thermal(preds)
    chart_multi = multi_material_comparison_chart(top_materials)

    # PDF Export
    pdf_path = 'static/recommendation.pdf'
    chart_bytes = io.BytesIO(base64.b64decode(chart_multi))
    export_recommendations_pdf(
        top_materials=top_materials,
        suitability_score=suitability_score,
        thermal_perf=thermal_perf,
        cost_est=cost_est,
        chart_img=chart_bytes,
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
        pdf_file_path=pdf_path
    )


@app.route('/download_pdf')
def download_pdf():
    """Serve the generated PDF"""
    pdf_path = 'static/recommendation.pdf'
    if not os.path.exists(pdf_path):
        return "PDF not found", 404
    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
