"""3D Model visualization component using Plotly for 3D rendering."""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Any


def create_box_mesh(center: List[float], size: List[float], color: List[float]):
    """Create vertices and faces for a box/cube."""
    x, y, z = center
    w, h, d = size
    
    # Box vertices
    vertices = np.array([
        [x - w/2, y - h/2, z - d/2],
        [x + w/2, y - h/2, z - d/2],
        [x + w/2, y + h/2, z - d/2],
        [x - w/2, y + h/2, z - d/2],
        [x - w/2, y - h/2, z + d/2],
        [x + w/2, y - h/2, z + d/2],
        [x + w/2, y + h/2, z + d/2],
        [x - w/2, y + h/2, z + d/2],
    ])
    
    return vertices, color


def render_3d_model(model_config: Dict[str, Any]):
    """
    Render 3D model visualization using Plotly.
    Simplified version using line traces for 3D structure.
    
    Args:
        model_config: Configuration dict with components, dimensions, etc.
    """
    
    fig = go.Figure()
    
    # Extract dimensions
    dims = model_config.get("dimensions", {})
    width = dims.get("width_cm", 30)
    depth = dims.get("depth_cm", 20)
    height = dims.get("height_cm", 15)
    thickness = dims.get("material_thickness_cm", 1)
    
    # Add components as wireframe
    components = model_config.get("components", [])
    
    for component in components:
        comp_type = component.get("type", "box")
        position = component.get("position", [0, 0, 0])
        color = component.get("color", [0.7, 0.7, 0.7])
        name = component.get("name", "Component")
        color_rgb = f'rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})'
        
        if comp_type == "box":
            size = component.get("size", [width, thickness, depth])
            vertices, _ = create_box_mesh(position, size, color)
            
            # Draw box edges as lines
            x, y, z = position
            w, h, d = size
            
            # Define edges of the box
            edges = [
                # Bottom face
                ([x-w/2, x+w/2], [y-h/2, y-h/2], [z-d/2, z-d/2]),
                ([x+w/2, x+w/2], [y-h/2, y+h/2], [z-d/2, z-d/2]),
                ([x+w/2, x-w/2], [y+h/2, y+h/2], [z-d/2, z-d/2]),
                ([x-w/2, x-w/2], [y+h/2, y-h/2], [z-d/2, z-d/2]),
                # Top face
                ([x-w/2, x+w/2], [y-h/2, y-h/2], [z+d/2, z+d/2]),
                ([x+w/2, x+w/2], [y-h/2, y+h/2], [z+d/2, z+d/2]),
                ([x+w/2, x-w/2], [y+h/2, y+h/2], [z+d/2, z+d/2]),
                ([x-w/2, x-w/2], [y+h/2, y-h/2], [z+d/2, z+d/2]),
                # Vertical edges
                ([x-w/2, x-w/2], [y-h/2, y-h/2], [z-d/2, z+d/2]),
                ([x+w/2, x+w/2], [y-h/2, y-h/2], [z-d/2, z+d/2]),
                ([x+w/2, x+w/2], [y+h/2, y+h/2], [z-d/2, z+d/2]),
                ([x-w/2, x-w/2], [y+h/2, y+h/2], [z-d/2, z+d/2]),
            ]
            
            for edge in edges:
                fig.add_trace(go.Scatter3d(
                    x=edge[0], y=edge[1], z=edge[2],
                    mode='lines',
                    line=dict(color=color_rgb, width=3),
                    name=name,
                    showlegend=True,
                    hoverinfo='name',
                ))
        
        elif comp_type == "cylinder":
            # Draw cylinder as circle outline
            cyl_height = component.get("dimensions", [1, height, 1])[1]
            cyl_radius = component.get("dimensions", [1, height, 1])[0]
            x, y, z = position
            
            # Draw two circles (top and bottom)
            theta = np.linspace(0, 2*np.pi, 32)
            
            # Bottom circle
            x_bottom = x + cyl_radius * np.cos(theta)
            y_bottom = np.full_like(theta, y - cyl_height/2)
            z_bottom = z + cyl_radius * np.sin(theta)
            
            fig.add_trace(go.Scatter3d(
                x=x_bottom, y=y_bottom, z=z_bottom,
                mode='lines',
                line=dict(color=color_rgb, width=3),
                name=name,
                showlegend=True,
                hoverinfo='name',
            ))
            
            # Top circle
            x_top = x + cyl_radius * np.cos(theta)
            y_top = np.full_like(theta, y + cyl_height/2)
            z_top = z + cyl_radius * np.sin(theta)
            
            fig.add_trace(go.Scatter3d(
                x=x_top, y=y_top, z=z_top,
                mode='lines',
                line=dict(color=color_rgb, width=3),
                name=name,
                showlegend=False,
                hoverinfo='name',
            ))
            
            # Draw vertical lines connecting circles
            for i in range(0, len(theta), 8):
                fig.add_trace(go.Scatter3d(
                    x=[x_bottom[i], x_top[i]],
                    y=[y_bottom[i], y_top[i]],
                    z=[z_bottom[i], z_top[i]],
                    mode='lines',
                    line=dict(color=color_rgb, width=2),
                    showlegend=False,
                    hoverinfo='skip',
                ))
    
    # Update layout
    fig.update_layout(
        title="3D Prototype Model",
        scene=dict(
            xaxis_title="Width (cm)",
            yaxis_title="Height (cm)",
            zaxis_title="Depth (cm)",
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            ),
        ),
        width=800,
        height=600,
        showlegend=True,
        hovermode='closest',
    )
    
    return fig


def display_3d_visualization(model_config: Dict[str, Any]):
    """Display the 3D model in Streamlit."""
    
    if not model_config:
        st.warning("No 3D model configuration available")
        return
    
    st.subheader("Interactive 3D Model")
    
    # Display dimensions
    dims = model_config.get("dimensions", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Width", f"{dims.get('width_cm', 0):.1f} cm")
    with col2:
        st.metric("Height", f"{dims.get('height_cm', 0):.1f} cm")
    with col3:
        st.metric("Depth", f"{dims.get('depth_cm', 0):.1f} cm")
    
    # Render 3D model
    fig = render_3d_model(model_config)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display components list
    st.subheader("Components")
    components = model_config.get("components", [])
    for i, component in enumerate(components, 1):
        with st.expander(f"{i}. {component.get('name', 'Component')}"):
            st.write(f"**Type:** {component.get('type', 'Unknown')}")
            st.write(f"**Material:** {component.get('material', 'Unknown')}")
            st.write(f"**Position:** {component.get('position', [0, 0, 0])}")
    
    # Display assembly notes
    assembly_notes = model_config.get("assembly_notes", [])
    if assembly_notes:
        st.subheader("Assembly Steps")
        for step in assembly_notes:
            st.write(f"• {step}")
    
    # Display materials
    materials = model_config.get("materials_used", [])
    if materials:
        st.subheader("Materials Used")
        st.write(", ".join(materials))
