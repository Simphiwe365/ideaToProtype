"""PDF generation utility for plan downloads."""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime


def generate_plan_pdf(request_data: dict, result_data: dict) -> bytes:
    """
    Generate a PDF document from the plan data using ReportLab.

    Args:
        request_data: The original request (idea, tools, materials, budget, skill level)
        result_data: The plan result (constrained_plan, unconstrained_plan, estimated_cost_zar)

    Returns:
        Raw PDF bytes suitable for Streamlit download buttons and tests.
    """
    # Create BytesIO object to store PDF
    pdf_buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=1,  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=8,
        spaceBefore=6,
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        leading=10,
    )
    
    # Build document elements
    elements = []
    
    # Title
    elements.append(Paragraph("Manufacturing Plan", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Project Details
    elements.append(Paragraph("PROJECT DETAILS", heading_style))
    detail_lines = [
        f"• Idea: {str(request_data.get('idea', 'N/A'))[:80]}",
        f"• Skill Level: {str(request_data.get('skill_level', 'N/A')).capitalize()}",
        f"• Budget: R{request_data.get('budget_zar', 0)}",
        f"• Tools: {', '.join(request_data.get('tools', []))[:80] or 'None'}",
        f"• Materials: {', '.join(request_data.get('materials', []))[:80] or 'None'}",
        f"• Estimated Cost: R{result_data.get('estimated_cost_zar', 0)}",
    ]
    for detail in detail_lines:
        elements.append(Paragraph(detail, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Constrained Plan
    elements.append(Paragraph("CONSTRAINED PLAN", heading_style))
    plan_text = result_data.get('constrained_plan', 'N/A')
    if len(plan_text) > 5000:
        plan_text = plan_text[:5000] + "\n\n[Plan truncated for PDF - see full plan in application]"
    elements.append(Paragraph(plan_text.replace('\n', '<br/>'), normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add page break
    elements.append(PageBreak())
    
    # Unconstrained Plan
    elements.append(Paragraph("UNCONSTRAINED PLAN", heading_style))
    plan_text_unconstrained = result_data.get('unconstrained_plan', 'N/A')
    if len(plan_text_unconstrained) > 5000:
        plan_text_unconstrained = plan_text_unconstrained[:5000] + "\n\n[Plan truncated for PDF - see full plan in application]"
    elements.append(Paragraph(plan_text_unconstrained.replace('\n', '<br/>'), normal_style))
    
    # Build PDF
    try:
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")


def get_pdf_filename(idea: str) -> str:
    """Generate a filename for the PDF based on the idea."""
    # Clean idea string for filename
    clean_idea = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in idea)
    clean_idea = clean_idea.replace(' ', '_')[:40]  # Limit to 40 chars
    if not clean_idea:
        clean_idea = "Plan"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{clean_idea}_{timestamp}.pdf"
