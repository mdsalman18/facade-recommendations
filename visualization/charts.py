import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Flask
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np

sns.set(style="whitegrid")  # clean white background with grid

def bar_chart_top_materials(top_materials):
    """
    Generates a grouped bar chart comparing Suitability, Thermal, and Cost for top materials.
    Returns the chart as a base64 string.
    """
    fig, ax = plt.subplots(figsize=(10,6))  # Increased figure size for more space

    # Extracting the material names and the corresponding values for scores, thermal, and cost
    materials = [m['material_type'] for m in top_materials]
    scores = [m['score'] for m in top_materials]
    thermal = [m['thermal'] for m in top_materials]
    cost = [m['cost'] for m in top_materials]

    bar_width = 0.25
    x = np.arange(len(materials))  # Using numpy array for x-ticks positioning

    # Plotting the bars for Suitability, Thermal, and Cost
    ax.bar(x, scores, width=bar_width, label='Suitability', color='steelblue')
    ax.bar(x + bar_width, thermal, width=bar_width, label='Thermal', color='orange')
    ax.bar(x + 2 * bar_width, cost, width=bar_width, label='Cost', color='green')

    # Adjusting x-ticks to be at the center of each set of bars
    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(materials, rotation=15)
    
    # Labeling the y-axis and title
    ax.set_ylabel('Value')
    ax.set_title('Top-3 Material Comparison')

    # Setting the y-axis limit to a bit higher than the maximum value for better spacing
    max_height = max(max(scores), max(thermal), max(cost))
    ax.set_ylim(0, max_height * 1.2)

    # Adding value labels above each bar
    for i in range(len(materials)):
        ax.text(x[i], scores[i] + max_height * 0.02, f'{scores[i]:.1f}', ha='center', fontsize=9)
        ax.text(x[i] + bar_width, thermal[i] + max_height * 0.02, f'{thermal[i]:.1f}', ha='center', fontsize=9)
        ax.text(x[i] + 2 * bar_width, cost[i] + max_height * 0.02, f'{cost[i]:.1f}', ha='center', fontsize=9)

    # Adding the legend for the different bars
    ax.legend()

    # Applying tight layout to adjust spacing and prevent overlap
    plt.tight_layout()

    # Saving the plot to a buffer and encoding as base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def scatter_cost_vs_thermal(materials_data):
    """
    Generates a scatter plot for Cost vs Thermal performance.
    Returns the chart as a base64 string.
    """
    fig, ax = plt.subplots(figsize=(6,4))

    costs = [m['cost'] for m in materials_data]
    thermal = [m['thermal'] for m in materials_data]
    labels = [m['material_type'] for m in materials_data]

    ax.scatter(thermal, costs, color='purple', s=100)

    for i, label in enumerate(labels):
        ax.annotate(label, (thermal[i], costs[i]), textcoords="offset points", xytext=(7,5),
                    ha='left', fontsize=9)

    ax.set_xlabel('Thermal Performance')
    ax.set_ylabel('Cost')
    ax.set_title('Cost vs Thermal Performance')

    ax.set_xlim(min(thermal)*0.95, max(thermal)*1.05)
    ax.set_ylim(min(costs)*0.95, max(costs)*1.15)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')
