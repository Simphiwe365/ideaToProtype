"""Results page displaying history of generated plans."""

from datetime import datetime

import streamlit as st
from utils.pdf_generator import generate_plan_pdf, get_pdf_filename


def _generate_download_content(request, result):
    """Generate downloadable plan content."""
    required_tools = request.get('tools', [])
    available_tools = request.get('available_tools', [])
    required_materials = request.get('materials', [])
    available_materials = request.get('available_materials', [])

    content = f"""LLM-Guided Manufacturing Plan
{'='*50}

IDEA: {request['idea']}
BUDGET: R{request['budget_zar']}
SKILL LEVEL: {request['skill_level'].capitalize()}

TOOLS REQUIRED:
{', '.join(required_tools)}

TOOLS ALREADY AVAILABLE:
{', '.join(available_tools) if available_tools else 'None'}

MATERIALS REQUIRED:
{', '.join(required_materials)}

MATERIALS ALREADY AVAILABLE:
{', '.join(available_materials) if available_materials else 'None'}

{'='*50}

CONSTRAINED PLAN (with your constraints):
{'-'*50}
{result['constrained_plan']}

{'='*50}

UNCONSTRAINED PLAN (ideal scenario):
{'-'*50}
{result['unconstrained_plan']}

{'='*50}
ESTIMATED COST: R{result['estimated_cost_zar']}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return content


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
        st.markdown(f"**Tools required:** {', '.join(request.get('tools', []))}")
        st.markdown(f"**Tools already available:** {', '.join(request.get('available_tools', [])) if request.get('available_tools') else 'None'}")
        st.markdown(f"**Materials required:** {', '.join(request.get('materials', []))}")
        st.markdown(f"**Materials already available:** {', '.join(request.get('available_materials', [])) if request.get('available_materials') else 'None'}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Constrained Plan")
            st.write(result["constrained_plan"])

        with col2:
            st.markdown("#### Unconstrained Plan")
            st.write(result["unconstrained_plan"])

        st.markdown(f"**Estimated Cost:** R{result['estimated_cost_zar']}")

        # Download button for this plan
        pdf_content = generate_plan_pdf(request, result)
        st.download_button(
            label=f"Download Plan {index} as PDF",
            data=pdf_content,
            file_name=get_pdf_filename(request["idea"]),
            mime="application/pdf",
            key=f"download_pdf_{index}"
        )

        st.download_button(
            label="📥 Download Plan as Text",
            data=_generate_download_content(request, result),
            file_name=f"plan_{index}_{request['idea'][:20].replace(' ', '_')}.txt",
            mime="text/plain",
        )

        st.divider()


if __name__ == "__main__":
    main()