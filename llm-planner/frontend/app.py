"""Streamlit application entry point with navigation."""

import streamlit as st
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