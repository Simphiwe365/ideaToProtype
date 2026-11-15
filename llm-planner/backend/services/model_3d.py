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


def parse_build_steps(plan_text: str) -> List[str]:
    """Extract build steps from the plan text."""
    steps = []
    
    # Look for numbered steps
    step_pattern = r'^\d+\.\s+(.+?)(?=^\d+\.|^[A-Z]+:|$)'
    matches = re.findall(step_pattern, plan_text, re.MULTILINE | re.DOTALL)
    
    if matches:
        steps = [step.strip() for step in matches]
    else:
        # Fallback: split by newlines and filter
        lines = plan_text.split('\n')
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                steps.append(line.strip())
    
    return steps[:6]  # Max 6 steps


def infer_component_type(step_text: str, materials: List[str]) -> str:
    """Infer component type from step description."""
    step_lower = step_text.lower()
    
    if any(word in step_lower for word in ['base', 'bottom', 'surface', 'platform', 'foundation']):
        return 'platform'
    elif any(word in step_lower for word in ['leg', 'support', 'stand', 'column']):
        return 'leg'
    elif any(word in step_lower for word in ['frame', 'structure', 'frame', 'skeleton']):
        return 'frame'
    elif any(word in step_lower for word in ['wall', 'side', 'panel', 'back']):
        return 'panel'
    elif any(word in step_lower for word in ['shelf', 'tier', 'level', 'rack']):
        return 'shelf'
    elif any(word in step_lower for word in ['bracket', 'joint', 'connector', 'brace']):
        return 'connector'
    else:
        return 'component'


def generate_3d_model_config(idea: str, plan_text: str, materials: List[str]) -> Dict[str, Any]:
    """
    Generate 3D model configuration for Three.js visualization.
    
    Now SMARTER - parses the actual plan to create accurate components.
    """
    
    dimensions = extract_dimensions_from_plan(plan_text, idea)
    steps = parse_build_steps(plan_text)
    
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
    
    # Generate components based on steps
    components = []
    component_index = 0
    
    for i, step in enumerate(steps):
        comp_type = infer_component_type(step, materials)
        
        if comp_type == 'platform':
            components.append({
                "id": "platform",
                "type": "box",
                "name": f"Platform/Base ({step[:30]}...)",
                "position": [0, dimensions["height"] - 1, 0],
                "size": [dimensions["width"], dimensions["thickness"], dimensions["depth"]],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
                "step": i + 1,
            })
        
        elif comp_type == 'leg':
            # Add 4 legs if not already added
            if not any(c["type"] == "leg" for c in components):
                leg_height = dimensions["height"] * 0.6
                leg_positions = [
                    [-dimensions["width"]/2 + 2, leg_height/2, -dimensions["depth"]/2 + 2],
                    [dimensions["width"]/2 - 2, leg_height/2, -dimensions["depth"]/2 + 2],
                    [-dimensions["width"]/2 + 2, leg_height/2, dimensions["depth"]/2 - 2],
                    [dimensions["width"]/2 - 2, leg_height/2, dimensions["depth"]/2 - 2],
                ]
                
                for j, pos in enumerate(leg_positions):
                    components.append({
                        "id": f"leg_{j+1}",
                        "type": "cylinder",
                        "name": f"Leg {j+1} ({step[:25]}...)",
                        "position": pos,
                        "dimensions": [0.8, leg_height, 0.8],
                        "color": primary_color,
                        "material": materials[0] if materials else "wood",
                        "step": i + 1,
                    })
        
        elif comp_type == 'panel':
            components.append({
                "id": f"panel_{component_index}",
                "type": "box",
                "name": f"Panel ({step[:30]}...)",
                "position": [0, dimensions["height"]/2, dimensions["depth"]/2],
                "size": [dimensions["width"] - 2, dimensions["height"] * 0.8, dimensions["thickness"]],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
                "step": i + 1,
            })
            component_index += 1
        
        elif comp_type == 'shelf':
            shelf_height = dimensions["height"] * (i / len(steps))
            components.append({
                "id": f"shelf_{component_index}",
                "type": "box",
                "name": f"Shelf/Level ({step[:25]}...)",
                "position": [0, shelf_height, 0],
                "size": [dimensions["width"] - 2, dimensions["thickness"], dimensions["depth"] - 2],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
                "step": i + 1,
            })
            component_index += 1
    
    # If no components were inferred, create default stand
    if not components:
        components = [
            {
                "id": "base_platform",
                "type": "box",
                "name": "Top Surface (Platform)",
                "position": [0, dimensions["height"], 0],
                "size": [dimensions["width"], dimensions["thickness"], dimensions["depth"]],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
                "step": 1,
            },
        ]
        
        # Add 4 legs
        leg_height = dimensions["height"] * 0.8
        leg_positions = [
            [-dimensions["width"]/2 + 2, leg_height/2, -dimensions["depth"]/2 + 2],
            [dimensions["width"]/2 - 2, leg_height/2, -dimensions["depth"]/2 + 2],
            [-dimensions["width"]/2 + 2, leg_height/2, dimensions["depth"]/2 - 2],
            [dimensions["width"]/2 - 2, leg_height/2, dimensions["depth"]/2 - 2],
        ]
        
        for j, pos in enumerate(leg_positions):
            components.append({
                "id": f"leg_{j+1}",
                "type": "cylinder",
                "name": f"Support Leg {j+1}",
                "position": pos,
                "dimensions": [1, leg_height, 1],
                "color": primary_color,
                "material": materials[0] if materials else "wood",
                "step": j + 2,
            })
    
    # Extract actual assembly notes from plan
    assembly_notes = []
    for i, step in enumerate(steps[:6], 1):
        # Clean up the step text
        clean_step = step.replace('\n', ' ').strip()
        # Limit to 100 chars
        if len(clean_step) > 100:
            clean_step = clean_step[:97] + "..."
        assembly_notes.append(f"{i}. {clean_step}")
    
    # Generate 3D model configuration
    model_config = {
        "type": "assembled_structure",
        "project_type": "stand" if "stand" in idea.lower() else "structure",
        "idea": idea,
        "dimensions": {
            "width_cm": dimensions["width"],
            "depth_cm": dimensions["depth"],
            "height_cm": dimensions["height"],
            "material_thickness_cm": dimensions["thickness"],
        },
        "components": components,
        "materials_used": materials,
        "assembly_notes": assembly_notes if assembly_notes else ["Follow the plan steps above"],
        "inferred_from_plan": True,
    }
    
    return model_config
