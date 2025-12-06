from fpdf import FPDF
import tempfile
import os

def export_recommendations_pdf(top_materials, suitability_score, thermal_perf, cost_est,
                               chart_img=None, glass_recommendations=None,
                               output_path='recommendation.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ------------------------
    # Phase 2: Top Materials
    # ------------------------
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Facade Material Recommendation", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Sustainability Score: {suitability_score}%", ln=True)
    pdf.cell(0, 10, f"Thermal Performance: {thermal_perf}", ln=True)
    pdf.cell(0, 10, f"Estimated Cost: {cost_est}", ln=True)
    pdf.ln(10)

    # Top materials table
    pdf.set_font("Arial", 'B', 12)
    top_material_widths = [50, 40, 40, 40]
    for i, col in enumerate(["Material", "Score", "Thermal", "Cost"]):
        pdf.cell(top_material_widths[i], 10, col, 1, align='C')
    pdf.ln()

    pdf.set_font("Arial", '', 12)
    for m in top_materials:
        for i, item in enumerate([m['material_type'], round(m['score'],2),
                                  round(m['thermal'],2), round(m['cost'],2)]):
            pdf.cell(top_material_widths[i], 10, str(item), 1, align='C')
        pdf.ln()

    # Insert chart image if provided
    if chart_img:
        chart_img.seek(0)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(chart_img.read())
                temp_path = temp_file.name
            pdf.ln(10)
            pdf.image(temp_path, x=30, w=150)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    # ------------------------
    # Phase 1: Glass Recommendations (Centered)
    # ------------------------
    if glass_recommendations:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Top Glass Options (Phase 1)", ln=True, align='C')
        pdf.ln(5)

        first_cols = ["Name", "Score", "U-Value", "SHGC", "VLT", "Acoustic", "Fire Rating"]
        second_cols = ["Cost", "Thickness", "Maintenance", "Solar Coating", "Impact", "Environmental"]
        first_col_widths = [40, 20, 20, 20, 20, 25, 25]
        second_col_widths = [25, 20, 25, 25, 25, 30]

        # Helper to print centered table
        def print_centered_table(columns, col_widths, data_rows, pdf):
            total_width = sum(col_widths)
            x_start = (pdf.w - total_width) / 2
            # Header
            pdf.set_font("Arial", 'B', 10)
            for i, col in enumerate(columns):
                pdf.set_x(x_start + sum(col_widths[:i]))
                pdf.cell(col_widths[i], 8, col, border=1, align='C')
            pdf.ln()
            # Rows
            pdf.set_font("Arial", '', 9)
            for row in data_rows:
                for i, item in enumerate(row):
                    pdf.set_x(x_start + sum(col_widths[:i]))
                    pdf.cell(col_widths[i], 6, str(item), border=1, align='C')
                pdf.ln()
            pdf.ln(5)

        # Prepare data for first table
        first_data = []
        for g in glass_recommendations:
            first_data.append([
                g.get("material_name", ""),
                round(g.get("score", 0),2),
                g.get("material_u_value", ""),
                g.get("material_shgc", ""),
                g.get("material_vlt_percent", ""),
                g.get("acoustic_rating_rw", ""),
                g.get("fire_rating", "")
            ])
        print_centered_table(first_cols, first_col_widths, first_data, pdf)

        # Prepare data for second table
        second_data = []
        for g in glass_recommendations:
            second_data.append([
                round(g.get("cost_per_sqm", 0),2),
                g.get("thickness_mm", ""),
                g.get("maintenance_freq_per_year", ""),
                g.get("solar_control_coating", ""),
                g.get("impact_resistance", ""),
                g.get("environmental_suitability", "")
            ])
        print_centered_table(second_cols, second_col_widths, second_data, pdf)

    pdf.output(output_path)
    return output_path
