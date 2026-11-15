"""Results page displaying history of generated plans."""

import re
from datetime import datetime

import streamlit as st

try:
    from frontend.utils.pdf_generator import generate_plan_pdf, get_pdf_filename
except ModuleNotFoundError:
    from utils.pdf_generator import generate_plan_pdf, get_pdf_filename


def clean_plan_text(plan_text: str) -> str:
    """Normalize raw LLM text for cleaner rendering in the results page."""
    if not plan_text:
        return ""

    cleaned = str(plan_text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    manufacturing_matches = list(re.finditer(r"(?m)^Manufacturing Plan\s*$", cleaned))
    if len(manufacturing_matches) > 1:
        cleaned = cleaned[manufacturing_matches[-1].start():].strip()

    if "CONSTRAINED PLAN" in cleaned and "UNCONSTRAINED PLAN" in cleaned:
        constrained_start = cleaned.index("CONSTRAINED PLAN")
        unconstrained_start = cleaned.index("UNCONSTRAINED PLAN")
        if unconstrained_start > constrained_start:
            cleaned = cleaned[constrained_start:unconstrained_start].rstrip()

    cleaned = re.sub(r"\*\*Estimated Cost:\*\*.*?\n?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"(?im)^\s*Estimated Cost:\s*R\d+(?:,\d{3})*(?:\.\d+)?\s*$", "", cleaned)
    cleaned = re.sub(r"(?im)^\s*ESTIMATED COST:\s*R\d+(?:,\d{3})*(?:\.\d+)?\s*$", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


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

        constrained_text = clean_plan_text(result.get("constrained_plan", ""))
        unconstrained_text = clean_plan_text(result.get("unconstrained_plan", ""))

        st.markdown("#### Constrained Plan")
        st.code(constrained_text, language="text")

        st.markdown("#### Unconstrained Plan")
        st.code(unconstrained_text, language="text")

        st.markdown(f"**Estimated Cost:** R{result['estimated_cost_zar']}")

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