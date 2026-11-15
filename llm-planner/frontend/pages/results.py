"""Results page displaying history of generated plans."""

import html
from datetime import datetime
from io import BytesIO

import streamlit as st
<<<<<<< HEAD
from utils.pdf_generator import generate_plan_pdf, get_pdf_filename
=======
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _clean_pdf_text(value):
    """Escape text so it can safely be rendered inside a PDF paragraph."""
    return html.escape(str(value or "")).replace("\n", "<br/>")


def generate_plan_pdf(request, result):
    """Build a PDF document for a generated manufacturing plan."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=18, leading=22, alignment=1, spaceAfter=12)
    heading_style = ParagraphStyle("CustomHeading", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=15, spaceAfter=8)
    body_style = ParagraphStyle("CustomBody", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=5)

    cost_breakdown = result.get("cost_breakdown", {})
    materials_to_buy = cost_breakdown.get("materials", [])
    tools_to_buy = cost_breakdown.get("tools", [])

    story = [
        Paragraph("LLM-Guided Manufacturing Plan", title_style),
        Paragraph(f"<b>Idea:</b> {_clean_pdf_text(request.get('idea', ''))}", body_style),
        Paragraph(f"<b>Budget:</b> R{request.get('budget_zar', '0')}", body_style),
        Paragraph(f"<b>Skill Level:</b> {request.get('skill_level', '').capitalize()}", body_style),
        Paragraph(f"<b>Tools Required:</b> {', '.join(request.get('tools', [])) or 'None'}", body_style),
        Paragraph(f"<b>Tools Already Available:</b> {', '.join(request.get('available_tools', [])) or 'None'}", body_style),
        Paragraph(f"<b>Materials Required:</b> {', '.join(request.get('materials', [])) or 'None'}", body_style),
        Paragraph(f"<b>Materials Already Available:</b> {', '.join(request.get('available_materials', [])) or 'None'}", body_style),
        Paragraph(f"<b>Estimated Cost:</b> R{result.get('estimated_cost_zar', '0')}", body_style),
        Spacer(1, 12),
        Paragraph("<b>Materials to Buy</b>", heading_style),
    ]

    if materials_to_buy:
        for item in materials_to_buy:
            story.append(Paragraph(f"- {_clean_pdf_text(item.get('name', ''))}: R{item.get('price', 0)}", body_style))
    else:
        story.append(Paragraph("- None", body_style))

    story.extend([
        Spacer(1, 8),
        Paragraph("<b>Tools to Buy</b>", heading_style),
    ])

    if tools_to_buy:
        for item in tools_to_buy:
            story.append(Paragraph(f"- {_clean_pdf_text(item.get('name', ''))}: R{item.get('price', 0)}", body_style))
    else:
        story.append(Paragraph("- None", body_style))

    story.extend([
        Spacer(1, 12),
        Paragraph("<b>Constrained Plan</b>", heading_style),
        Paragraph(_clean_pdf_text(result.get("constrained_plan", "")), body_style),
        Spacer(1, 12),
        Paragraph("<b>Unconstrained Plan</b>", heading_style),
        Paragraph(_clean_pdf_text(result.get("unconstrained_plan", "")), body_style),
        Spacer(1, 12),
        Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style),
    ])

    doc.build(story)
    return buffer.getvalue()


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
>>>>>>> 6b53d89 (Add unit tests for API client functions and plan PDF generation)


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
<<<<<<< HEAD
        
        # Download button for this plan
        pdf_content = generate_plan_pdf(request, result)
        st.download_button(
            label=f"Download Plan {index} as PDF",
            data=pdf_content,
            file_name=get_pdf_filename(request["idea"]),
            mime="application/pdf",
            key=f"download_pdf_{index}"
        )
        
=======

        st.download_button(
            label="📄 Download Plan as PDF",
            data=generate_plan_pdf(request, result),
            file_name=f"plan_{index}_{request['idea'][:20].replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

        st.download_button(
            label="📥 Download Plan as Text",
            data=_generate_download_content(request, result),
            file_name=f"plan_{index}_{request['idea'][:20].replace(' ', '_')}.txt",
            mime="text/plain",
        )

>>>>>>> 6b53d89 (Add unit tests for API client functions and plan PDF generation)
        st.divider()


if __name__ == "__main__":
    main()