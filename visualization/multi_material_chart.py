import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Flask
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import numpy as np

sns.set(style="whitegrid")

def multi_material_comparison_chart(top_materials):
    """
    Generates a grouped bar chart comparing Suitability, Thermal, and Cost for top materials.
    Returns the chart as a BytesIO object (ready for PDF export).
    """
    if not top_materials:
        raise ValueError("top_materials list is empty")

    # Create a DataFrame from the input data
    df = pd.DataFrame(top_materials)

    # Ensure necessary columns exist
    for col in ['score', 'thermal', 'cost', 'material_type']:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Normalize cost and thermal to 0-100 scale safely
    df['cost_norm'] = 100 * (df['cost'] - df['cost'].min()) / (df['cost'].max() - df['cost'].min() + 1e-8)
    df['thermal_norm'] = 100 * (df['thermal'] - df['thermal'].min()) / (df['thermal'].max() - df['thermal'].min() + 1e-8)

    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(12, 7))

    bar_width = 0.2
    x = np.arange(len(df['material_type']))

    # Plotting the bars
    ax.bar(x, df['score'], width=bar_width, label='Suitability', color='steelblue')
    ax.bar(x + bar_width, df['thermal_norm'], width=bar_width, label='Thermal', color='orange')
    ax.bar(x + 2 * bar_width, df['cost_norm'], width=bar_width, label='Cost', color='green')

    # Adjust x-ticks
    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(df['material_type'], rotation=15)

    # Label axes and title
    ax.set_ylabel('Normalized Score / Percentage')
    ax.set_xlabel('Material Type')
    ax.set_title('Top Materials Comparison')

    # Set y-axis limit
    max_value = max(df['score'].max(), df['thermal_norm'].max(), df['cost_norm'].max())
    ax.set_ylim(0, max_value * 1.2)

    # Add value labels above each bar
    for i in range(len(df['material_type'])):
        ax.text(x[i], df['score'][i] + max_value * 0.03, f'{df["score"][i]:.1f}', ha='center', fontsize=9)
        ax.text(x[i] + bar_width, df['thermal_norm'][i] + max_value * 0.03, f'{df["thermal_norm"][i]:.1f}', ha='center', fontsize=9)
        ax.text(x[i] + 2 * bar_width, df['cost_norm'][i] + max_value * 0.03, f'{df["cost_norm"][i]:.1f}', ha='center', fontsize=9)

    # Add legend
    ax.legend(title="Metric", loc='upper left', bbox_to_anchor=(1, 1), fontsize=10, title_fontsize=11)

    plt.tight_layout()

    # Save figure to BytesIO for PDF export
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf  # Return BytesIO directly instead of base64
