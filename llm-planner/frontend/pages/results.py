"""Results page displaying history of generated plans."""

import streamlit as st


def main():
    """Render the results/history page."""
    st.title("Plan History")

    if "history" not in st.session_state or not st.session_state["history"]:
        st.info("No plans generated yet. Go to the Planner page to create your first plan.")
        return

    for index, entry in enumerate(st.session_state["history"], start=1):
        request = entry["request"]
        result = entry["result"]

        st.markdown(f"### Plan {index}: {request['idea']}")
        st.markdown(f"**Budget:** R{request['budget_zar']}  •  **Skill:** {request['skill_level'].capitalize()}")
        st.markdown(f"**Tools:** {', '.join(request['tools'])}")
        st.markdown(f"**Materials:** {', '.join(request['materials'])}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Constrained Plan")
            st.write(result["constrained_plan"]) 

        with col2:
            st.markdown("#### Unconstrained Plan")
            st.write(result["unconstrained_plan"])

        st.markdown(f"**Estimated Cost:** R{result['estimated_cost_zar']}")
        st.divider()


if __name__ == "__main__":
    main()