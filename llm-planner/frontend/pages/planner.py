"""Main planner page for inputting constraints and displaying generated plans."""

import streamlit as st
from components.constraint_form import constraint_form
from api_client import get_plan


def _render_plan_overview(result: dict[str, any]) -> None:
    """Render the plan overview section with cost and comparison note."""
    heading_col, cost_col, note_col = st.columns([2, 1, 2])

    with heading_col:
        st.markdown("#### Plan Actions")
        st.markdown(f"**{len(result['steps'])} steps generated**")

    with cost_col:
        st.metric("Estimated Cost", f"R{result['estimated_cost_zar']}")

    with note_col:
        st.markdown("#### Comparison Note")
        st.markdown(
            "This constrained plan aims for resource efficiency within your budget and tool availability. "
            "The unconstrained plan offers creative alternatives with potentially different costs and skill requirements."
        )


def _render_plan_results(result: dict[str, any]) -> None:
    """Render the constrained and unconstrained plan sections."""
    table_col, plan_col = st.columns([1, 1])

    with table_col:
        st.markdown("#### Constrained Plan Steps")
        for index, step in enumerate(result["steps"], start=1):
            st.write(f"**Step {index}:** {step}")

    with plan_col:
        st.markdown("#### Unconstrained Plan")
        st.write(result["unconstrained_plan"])

    st.markdown("---")

    st.markdown("#### Constrained Plan Details")
    st.write(result["constrained_plan"])


def main():
    """Render the planner page."""
    st.title("Maker Planner")
    st.markdown("Use the form below to generate a constrained manufacturing plan and compare it with a more open-ended approach.")

    data = constraint_form()

    if data:
        try:
            result = get_plan(data)

            if "history" not in st.session_state:
                st.session_state["history"] = []

            st.session_state["history"].insert(0, {
                "request": data,
                "result": result,
            })

            _render_plan_overview(result)
            _render_plan_results(result)

        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")


if __name__ == "__main__":
    main()