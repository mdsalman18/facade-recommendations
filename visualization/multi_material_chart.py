import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Flask
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64

sns.set(style="whitegrid")

def multi_material_comparison_chart(top_materials):
    """
    Generates a grouped bar chart comparing Suitability, Thermal, and Cost for top materials.
    The chart is normalized and returns as a base64 PNG string.
    """
    # Create a DataFrame from the input data
    df = pd.DataFrame(top_materials)

    # Normalize cost and thermal to 0-100 scale
    if df['cost'].max() != df['cost'].min():
        df['cost_norm'] = 100 * (df['cost'] - df['cost'].min()) / (df['cost'].max() - df['cost'].min())
    else:
        df['cost_norm'] = 100
    if df['thermal'].max() != df['thermal'].min():
        df['thermal_norm'] = 100 * (df['thermal'] - df['thermal'].min()) / (df['thermal'].max() - df['thermal'].min())
    else:
        df['thermal_norm'] = 100

    # Melt the DataFrame to get it in a long format suitable for plotting
    df_melt = pd.melt(df, id_vars=['material_type'], 
                      value_vars=['score', 'thermal_norm', 'cost_norm'],
                      var_name='Metric', value_name='Value')

    # Mapping the metrics to more readable labels
    metric_labels = {'score': 'Suitability', 'thermal_norm': 'Thermal', 'cost_norm': 'Cost'}
    df_melt['Metric'] = df_melt['Metric'].map(metric_labels)

    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(12, 7))  # Increased figure size for better readability

    # Use seaborn to create a grouped barplot
    bar_width = 0.2  # Reduced width for better spacing
    x = range(len(df['material_type']))  # X-axis positions for the bars

    # Plotting the bars for each metric (Suitability, Thermal, Cost)
    ax.bar(x, df['score'], width=bar_width, label='Suitability', color='steelblue')
    ax.bar([i + bar_width for i in x], df['thermal_norm'], width=bar_width, label='Thermal', color='orange')
    ax.bar([i + 2 * bar_width for i in x], df['cost_norm'], width=bar_width, label='Cost', color='green')

    # Adjust the x-ticks to be at the center of the grouped bars
    ax.set_xticks([i + bar_width for i in x])
    ax.set_xticklabels(df['material_type'], rotation=15)
    
    # Labeling axes
    ax.set_ylabel('Normalized Score / Percentage')
    ax.set_xlabel('Material Type')
    ax.set_title('Top Materials Comparison')

    # Setting y-axis limit to give extra space at the top for labels
    max_value = max(df['score'].max(), df['thermal_norm'].max(), df['cost_norm'].max())
    ax.set_ylim(0, max_value * 1.2)

    # Add value labels above each bar
    for i in range(len(df['material_type'])):
        ax.text(x[i], df['score'][i] + max_value * 0.03, f'{df["score"][i]:.1f}', ha='center', fontsize=9)
        ax.text(x[i] + bar_width, df['thermal_norm'][i] + max_value * 0.03, f'{df["thermal_norm"][i]:.1f}', ha='center', fontsize=9)
        ax.text(x[i] + 2 * bar_width, df['cost_norm'][i] + max_value * 0.03, f'{df["cost_norm"][i]:.1f}', ha='center', fontsize=9)

    # Add the legend and move it outside the plot to avoid overlap
    ax.legend(title="Metric", loc='upper left', bbox_to_anchor=(1, 1), fontsize=10, title_fontsize=11)

    # Apply tight layout to ensure no overlap
    plt.tight_layout()

    # Save the figure to a buffer and encode as base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return base64.b64encode(buf.getvalue()).decode('utf-8')
