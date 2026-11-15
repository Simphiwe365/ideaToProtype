"""Streamlit application entry point with navigation."""

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from frontend.pages.planner import main as planner_main
    from frontend.pages.results import main as results_main
except ModuleNotFoundError:
    from pages.planner import main as planner_main
    from pages.results import main as results_main

st.set_page_config(
    page_title="Maker Planner",
    layout="wide",
    page_icon="🔧"
)

# Sidebar branding
st.sidebar.title("LLM-Guided Micro-Manufacturing Planner")
st.sidebar.markdown("**Honours Computer Science Research Project**")
st.sidebar.markdown("University of Zululand")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio("Navigate", ["Planner", "Results"])

if page == "Planner":
    planner_main()
elif page == "Results":
    results_main()