from fpdf import FPDF
import base64
from io import BytesIO
import tempfile
import os

def export_recommendations_pdf(top_materials, suitability_score, thermal_perf, cost_est, chart_img=None, output_path='recommendation.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Facade Material Recommendation", ln=True, align='C')
    pdf.ln(10)

    # Summary
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Sustainability Score: {suitability_score}%", ln=True)
    pdf.cell(0, 10, f"Thermal Performance: {thermal_perf}", ln=True)
    pdf.cell(0, 10, f"Estimated Cost: {cost_est}", ln=True)
    pdf.ln(10)

    # Top materials table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Material", 1)
    pdf.cell(40, 10, "Score", 1)
    pdf.cell(40, 10, "Thermal", 1)
    pdf.cell(40, 10, "Cost", 1)
    pdf.ln()

    pdf.set_font("Arial", '', 12)
    for m in top_materials:
        pdf.cell(50, 10, str(m['material_type']), 1)
        pdf.cell(40, 10, str(round(m['score'], 2)), 1)
        pdf.cell(40, 10, str(round(m['thermal'], 2)), 1)
        pdf.cell(40, 10, str(round(m['cost'], 2)), 1)
        pdf.ln()

    # Insert chart image (chart_img = BytesIO)
    if chart_img:
        # Save BytesIO image to a temp PNG file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(chart_img.getvalue())
        temp_file.close()

        pdf.ln(10)
        pdf.image(temp_file.name, x=30, w=150)

        # Remove temp file
        os.remove(temp_file.name)

    pdf.output(output_path)
    return output_path
