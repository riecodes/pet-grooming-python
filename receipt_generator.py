from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

ACCENT_COLOR = colors.HexColor('#3b8ed0')
MASCOT_EMOJI = '🐶'


def generate_receipt(customer_name, services, total_amount, output_path, address=None, phone=None, pet_name=None, pet_type=None, breed=None, num_pets=None):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=ACCENT_COLOR,
        spaceAfter=10,
        alignment=1  # Center
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.black,
        spaceAfter=20,
        alignment=1
    )
    normal_center = ParagraphStyle(
        'NormalCenter',
        parent=styles['Normal'],
        alignment=1,
        fontSize=12
    )
    # Mascot/Logo
    elements.append(Paragraph(f'<font size=36>{MASCOT_EMOJI}</font>', normal_center))
    # Title
    elements.append(Paragraph("PawBuddy Grooming Services", title_style))
    elements.append(Paragraph("Receipt", subtitle_style))
    elements.append(Spacer(1, 10))
    # Customer info
    elements.append(Paragraph(f"<b>Customer:</b> {customer_name}", styles["Normal"]))
    if address:
        elements.append(Paragraph(f"<b>Address:</b> {address}", styles["Normal"]))
    if phone:
        elements.append(Paragraph(f"<b>Phone:</b> {phone}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    # Pet info
    if pet_name or pet_type or breed or num_pets:
        pet_details = []
        if pet_name:
            pet_details.append(f"<b>Pet Name:</b> {pet_name}")
        if pet_type:
            pet_details.append(f"<b>Pet Type:</b> {pet_type}")
        if breed:
            pet_details.append(f"<b>Breed:</b> {breed}")
        if num_pets:
            pet_details.append(f"<b>Number of Pets:</b> {num_pets}")
        elements.append(Paragraph("  ".join(pet_details), styles["Normal"]))
    elements.append(Spacer(1, 16))
    # Service table
    data = [['Service', 'Price (PHP)']]
    for service, price in services:
        data.append([service, f"P{price:.2f}"])
    data.append(['Total', f"P{total_amount:.2f}"])
    table = Table(data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 12),
        ('GRID', (0, 0), (-1, -1), 1, ACCENT_COLOR),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), ACCENT_COLOR),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))
    # Friendly footer
    elements.append(Paragraph("<b>Thank you for choosing PawBuddy!</b>", normal_center))
    elements.append(Paragraph("We hope to see you and your pet again soon!", normal_center))
    doc.build(elements) 