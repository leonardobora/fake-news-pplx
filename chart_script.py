import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Define the components with better positioning and full names within 15 char limit
components = {
    "Streamlit UI": {"type": "ui", "pos": (1, 3)},
    "User Input": {"type": "input", "pos": (2, 3)},
    "Content Agent": {"type": "agent", "pos": (3, 4)},
    "Fact Agent": {"type": "agent", "pos": (4, 4.5)},
    "Source Agent": {"type": "agent", "pos": (4, 1.5)},
    "Perplexity API": {"type": "external", "pos": (5, 4.5)},
    "Final Agent": {"type": "agent", "pos": (6, 3)},
    "News Result": {"type": "output", "pos": (7, 3)}
}

# Define flows including the missing Streamlit UI connection
flows = [
    ("Streamlit UI", "User Input"),
    ("User Input", "Content Agent"),
    ("Content Agent", "Fact Agent"),
    ("Content Agent", "Source Agent"),
    ("Fact Agent", "Perplexity API"),
    ("Perplexity API", "Final Agent"),
    ("Source Agent", "Final Agent"),
    ("Fact Agent", "Final Agent"),
    ("Final Agent", "News Result")
]

# Color mapping for component types
colors = {
    "ui": "#1FB8CD",
    "input": "#DB4545", 
    "agent": "#2E8B57",
    "external": "#5D878F",
    "output": "#D2BA4C"
}

# Create figure
fig = go.Figure()

# Add connections (edges) with improved arrows
for start, end in flows:
    x0, y0 = components[start]["pos"]
    x1, y1 = components[end]["pos"]
    
    # Add line
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[y0, y1],
        mode='lines',
        line=dict(color='#666666', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add arrowhead
    dx = x1 - x0
    dy = y1 - y0
    length = np.sqrt(dx**2 + dy**2)
    
    if length > 0:
        # Normalize direction
        dx_norm = dx / length
        dy_norm = dy / length
        
        # Arrow position (85% along the line)
        arrow_x = x0 + 0.85 * dx
        arrow_y = y0 + 0.85 * dy
        
        # Arrow size
        arrow_size = 0.15
        
        # Arrow points
        arrow_x_points = [
            arrow_x,
            arrow_x - arrow_size * dx_norm - arrow_size * dy_norm * 0.6,
            arrow_x - arrow_size * dx_norm + arrow_size * dy_norm * 0.6,
            arrow_x
        ]
        arrow_y_points = [
            arrow_y,
            arrow_y - arrow_size * dy_norm + arrow_size * dx_norm * 0.6,
            arrow_y - arrow_size * dy_norm - arrow_size * dx_norm * 0.6,
            arrow_y
        ]
        
        fig.add_trace(go.Scatter(
            x=arrow_x_points, y=arrow_y_points,
            mode='lines',
            fill='toself',
            fillcolor='#666666',
            line=dict(color='#666666', width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

# Add nodes with better sizing and positioning
legend_added = set()
for name, info in components.items():
    x, y = info["pos"]
    color = colors[info["type"]]
    
    # Create legend name only once per type
    legend_name = info["type"].title()
    show_legend = legend_name not in legend_added
    if show_legend:
        legend_added.add(legend_name)
    
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers+text',
        marker=dict(
            size=80,
            color=color,
            line=dict(color='white', width=3)
        ),
        text=[name],
        textposition='middle center',
        textfont=dict(size=11, color='white', family='Arial Black'),
        name=legend_name,
        showlegend=show_legend,
        hovertemplate=f"<b>{name}</b><br>Type: {info['type'].title()}<extra></extra>"
    ))

# Add decision point indicators for branching nodes
decision_nodes = ["Content Agent", "Final Agent"]
for node_name in decision_nodes:
    if node_name in components:
        x, y = components[node_name]["pos"]
        # Add small diamond indicator
        fig.add_trace(go.Scatter(
            x=[x], y=[y-0.6],
            mode='markers',
            marker=dict(
                size=20,
                color='white',
                symbol='diamond',
                line=dict(color='#666666', width=2)
            ),
            showlegend=False,
            hoverinfo='skip'
        ))

# Update layout with better spacing
fig.update_layout(
    title="Fake News Detection System Flow",
    showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    plot_bgcolor='white'
)

# Set proper axis ranges with better spacing
fig.update_xaxes(range=[0.5, 7.5])
fig.update_yaxes(range=[0.5, 5.5])

# Save the chart
fig.write_image("system_architecture.png")