"""Reusable Streamlit component for the constraint input form."""

import streamlit as st
from typing import Any, Dict


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
                "Tools",
                ["hand tools", "3D printer", "drill", "soldering iron", "laser cutter", "none"],
                default=["hand tools"],
            )

        with materials_column:
            materials = st.multiselect(
                "Materials",
                ["wood", "cardboard", "PLA filament", "metal", "plastic sheet", "fabric"],
                default=["wood"],
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
                "materials": materials,
                "budget_zar": budget_zar,
                "skill_level": skill_level,
            }

    return {}