"""3D model generation service for prototype visualization."""

import json
import re
from typing import Dict, List, Any


def extract_dimensions_from_plan(plan_text: str, idea: str) -> Dict[str, float]:
    """Extract estimated dimensions from the plan text."""
    dimensions = {
        "width": 30.0,      # cm
        "depth": 20.0,      # cm
        "height": 15.0,     # cm
        "thickness": 1.0,   # cm (material thickness)
    }
    
    # Try to extract dimensions from plan text
    # Look for patterns like "30cm", "300mm", etc
    patterns = [
        r'(\d+)\s*(?:cm|centimeter)',
        r'(\d+)\s*(?:mm|millimeter)',
        r'(\d+)\s*(?:inches|inch|")',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, plan_text.lower())
        if matches:
            try:
                val = float(matches[0])
                # Convert to cm if needed
                if "mm" in pattern:
                    val = val / 10
                if "inch" in pattern:
                    val = val * 2.54
                dimensions["width"] = val
                break
            except:
                pass
    
    return dimensions


def generate_3d_model_config(idea: str, plan_text: str, materials: List[str]) -> Dict[str, Any]:
    """
    Generate 3D model configuration for Three.js visualization.
    
    Returns a config that describes:
    - Base platform/surface
    - Support legs/structure
    - Material colors
    - Dimensions
    """
    
    dimensions = extract_dimensions_from_plan(plan_text, idea)
    
    # Map materials to colors (RGB)
    material_colors = {
        "wood": [0.82, 0.71, 0.55],      # Wood brown
        "metal": [0.50, 0.50, 0.50],     # Metal gray
        "plastic": [0.80, 0.80, 0.80],   # Plastic light gray
        "steel": [0.40, 0.40, 0.40],     # Steel dark gray
        "aluminum": [0.75, 0.75, 0.75],  # Aluminum light gray
        "paint": [0.90, 0.90, 0.90],     # Paint white/neutral
        "default": [0.70, 0.70, 0.70],   # Default gray
    }
    
    # Determine primary material color
    primary_color = material_colors["default"]
    for material in materials:
        for key, color in material_colors.items():
            if key.lower() in material.lower():
                primary_color = color
                break
    
    # Generate 3D model configuration
    # For a laptop stand: base platform + 4 legs
    model_config = {
        "type": "assembled_structure",
        "project_type": "stand" if "stand" in idea.lower() else "structure",
        "dimensions": {
            "width_cm": dimensions["width"],
            "depth_cm": dimensions["depth"],
            "height_cm": dimensions["height"],
            "material_thickness_cm": dimensions["thickness"],
        },
        "components": [
            {
                "id": "base_platform",
                "type": "box",
                "name": "Top Surface (Platform)",
                "position": [0, dimensions["height"], 0],
                "size": [dimensions["width"], dimensions["thickness"], dimensions["depth"]],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
            },
            {
                "id": "leg_1",
                "type": "cylinder",
                "name": "Front Left Leg",
                "position": [
                    -dimensions["width"]/2 + 2,
                    dimensions["height"]/2,
                    -dimensions["depth"]/2 + 2
                ],
                "dimensions": [1, dimensions["height"], 1],  # radius, height, radius
                "color": primary_color,
                "material": materials[0] if materials else "wood",
            },
            {
                "id": "leg_2",
                "type": "cylinder",
                "name": "Front Right Leg",
                "position": [
                    dimensions["width"]/2 - 2,
                    dimensions["height"]/2,
                    -dimensions["depth"]/2 + 2
                ],
                "dimensions": [1, dimensions["height"], 1],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
            },
            {
                "id": "leg_3",
                "type": "cylinder",
                "name": "Back Left Leg",
                "position": [
                    -dimensions["width"]/2 + 2,
                    dimensions["height"]/2,
                    dimensions["depth"]/2 - 2
                ],
                "dimensions": [1, dimensions["height"], 1],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
            },
            {
                "id": "leg_4",
                "type": "cylinder",
                "name": "Back Right Leg",
                "position": [
                    dimensions["width"]/2 - 2,
                    dimensions["height"]/2,
                    dimensions["depth"]/2 - 2
                ],
                "dimensions": [1, dimensions["height"], 1],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
            },
        ],
        "materials_used": materials,
        "assembly_notes": [
            "1. Prepare all wood pieces by cutting to dimension",
            "2. Sand all surfaces smooth",
            "3. Assemble legs to base platform",
            "4. Apply finish/paint if needed",
            "5. Allow to cure before use",
        ],
    }
    
    return model_config
