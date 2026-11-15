"""Reusable Streamlit component for the constraint input form."""

import streamlit as st
from typing import Any, Dict


def _split_custom_items(raw_value: str) -> list[str]:
    """Split a comma-separated custom item text field into clean values."""
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def constraint_form() -> Dict[str, Any]:
    """Render the constraint input form and return the collected data."""
    with st.form("constraint_form"):
        st.markdown("#### Project Inputs")

        idea = st.text_area(
            "Product Idea",
            placeholder="Describe your project idea...",
            height=150,
        )

        tools_column, materials_column, meta_column = st.columns([2, 2, 1])

        with tools_column:
            tools = st.multiselect(
                "Tools needed",
                ["hand tools", "3D printer", "drill", "soldering iron", "laser cutter", "none"],
                default=["hand tools"],
            )
            available_tools = st.multiselect(
                "Tools you already have",
                ["hand tools", "3D printer", "drill", "soldering iron", "laser cutter", "none"],
                default=[],
            )
            custom_available_tools = st.text_input(
                "Other tools you already have (comma separated)",
                placeholder="angle grinder, bench vise",
            )

        with materials_column:
            materials = st.multiselect(
                "Materials needed",
                ["wood", "cardboard", "PLA filament", "metal", "plastic sheet", "fabric"],
                default=["wood"],
            )
            available_materials = st.multiselect(
                "Materials you already have",
                ["wood", "cardboard", "PLA filament", "metal", "plastic sheet", "fabric"],
                default=[],
            )
            custom_available_materials = st.text_input(
                "Other materials you already have (comma separated)",
                placeholder="steel plate, acrylic, resin",
            )

        with meta_column:
            skill_level = st.radio(
                "Skill Level",
                ["beginner", "intermediate", "advanced"],
                index=0,
                horizontal=True,
            )

            budget_zar = st.slider(
                "Budget (ZAR)",
                min_value=100,
                max_value=2000,
                value=500,
                step=50,
            )

        st.markdown("---")

        submitted = st.form_submit_button("Generate Plan")

        if submitted:
            return {
                "idea": idea,
                "tools": tools,
                "available_tools": list(dict.fromkeys([*available_tools, *_split_custom_items(custom_available_tools)])),
                "materials": materials,
                "available_materials": list(dict.fromkeys([*available_materials, *_split_custom_items(custom_available_materials)])),
                "budget_zar": budget_zar,
                "skill_level": skill_level,
            }

    return {}