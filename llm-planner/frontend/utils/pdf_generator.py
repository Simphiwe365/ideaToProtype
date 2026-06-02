"""PDF generation utility for plan downloads."""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime


def generate_plan_pdf(request_data: dict, result_data: dict) -> BytesIO:
    """
    Generate a PDF document from the plan data using ReportLab.
    
    Args:
        request_data: The original request (idea, tools, materials, budget, skill level)
        result_data: The plan result (constrained_plan, unconstrained_plan, estimated_cost_zar)
    
    Returns:
        BytesIO object containing the PDF content
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
    
    detail_data = [
        ["Field", "Value"],
        ["Idea", str(request_data.get('idea', 'N/A'))[:80]],
        ["Skill Level", str(request_data.get('skill_level', 'N/A')).capitalize()],
        ["Budget", f"R{request_data.get('budget_zar', 0)}"],
        ["Tools", ', '.join(request_data.get('tools', []))[:80]],
        ["Materials", ', '.join(request_data.get('materials', []))[:80]],
        ["Estimated Cost", f"R{result_data.get('estimated_cost_zar', 0)}"],
    ]
    
    detail_table = Table(detail_data, colWidths=[1.5*inch, 4*inch])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(detail_table)
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
        return pdf_buffer
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
