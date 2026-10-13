import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class CertificatePDFGenerator:
    """
    Generates professional, high-resolution vector PDF certificates
    using ReportLab.
    """

    @classmethod
    def generate(cls, user_name, certificate_id, issue_date_str, course_name="Linux Commands Learning Assistant", verification_hash=None):
        buffer = io.BytesIO()
        width, height = landscape(letter)  # 11 x 8.5 inches -> 792 x 612 pt

        c = canvas.Canvas(buffer, pagesize=landscape(letter))
        c.setTitle(f"Certificate_{certificate_id}")

        # -----------------------------------------------------------
        # 1. Background and Borders
        # -----------------------------------------------------------
        # Dark luxurious slate border & cream/parchment background
        c.setFillColor(colors.HexColor("#0B132B"))
        c.rect(0, 0, width, height, fill=True, stroke=False)

        # Outer glowing accent border
        c.setStrokeColor(colors.HexColor("#10B981"))  # Terminal emerald
        c.setLineWidth(3)
        c.rect(18, 18, width - 36, height - 36, fill=False, stroke=True)

        # Inner gold/silver frame
        c.setStrokeColor(colors.HexColor("#38BDF8"))  # Cyan accent
        c.setLineWidth(1)
        c.rect(26, 26, width - 52, height - 52, fill=False, stroke=True)

        # Subtle dark card body
        c.setFillColor(colors.HexColor("#1C2541"))
        c.roundRect(36, 36, width - 72, height - 72, 8, fill=True, stroke=False)

        # Corner decorations
        c.setStrokeColor(colors.HexColor("#10B981"))
        c.setLineWidth(2)
        corner_size = 28
        # Top-left
        c.line(44, height - 44, 44 + corner_size, height - 44)
        c.line(44, height - 44, 44, height - 44 - corner_size)
        # Top-right
        c.line(width - 44, height - 44, width - 44 - corner_size, height - 44)
        c.line(width - 44, height - 44, width - 44, height - 44 - corner_size)
        # Bottom-left
        c.line(44, 44, 44 + corner_size, 44)
        c.line(44, 44, 44, 44 + corner_size)
        # Bottom-right
        c.line(width - 44, 44, width - 44 - corner_size, 44)
        c.line(width - 44, 44, width - 44, 44 + corner_size)

        # -----------------------------------------------------------
        # 2. Header & Branding
        # -----------------------------------------------------------
        c.setFillColor(colors.HexColor("#10B981"))
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2.0, height - 75, "LINUX COMMANDS LEARNING PLATFORM")

        c.setFillColor(colors.HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width / 2.0, height - 115, "CERTIFICATE OF MASTERY")

        c.setStrokeColor(colors.HexColor("#10B981"))
        c.setLineWidth(1.5)
        c.line(width / 2.0 - 140, height - 128, width / 2.0 + 140, height - 128)

        # -----------------------------------------------------------
        # 3. Recipient Information
        # -----------------------------------------------------------
        c.setFillColor(colors.HexColor("#94A3B8"))
        c.setFont("Helvetica", 13)
        c.drawCentredString(width / 2.0, height - 165, "THIS IS PROUDLY PRESENTED TO")

        # Student Name
        c.setFillColor(colors.HexColor("#38BDF8"))
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(width / 2.0, height - 215, user_name.upper())

        # Underline under name
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(1)
        c.line(width / 2.0 - 200, height - 228, width / 2.0 + 200, height - 228)

        # -----------------------------------------------------------
        # 4. Certification Statement
        # -----------------------------------------------------------
        c.setFillColor(colors.HexColor("#E2E8F0"))
        c.setFont("Helvetica", 12)
        statement1 = "for successfully fulfilling all requirements, passing practical assessments, and demonstrating"
        statement2 = f"exceptional competency in Linux command line operations and systems administration in"
        c.drawCentredString(width / 2.0, height - 265, statement1)
        c.drawCentredString(width / 2.0, height - 285, statement2)

        c.setFillColor(colors.HexColor("#10B981"))
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 320, course_name)

        # -----------------------------------------------------------
        # 5. Metadata Badges (Certificate ID, Date, Verification)
        # -----------------------------------------------------------
        box_y = 110
        box_h = 75
        box_w = 190

        # Badge 1: Issue Date
        c.setFillColor(colors.HexColor("#0F172A"))
        c.roundRect(70, box_y, box_w, box_h, 6, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor("#334155"))
        c.roundRect(70, box_y, box_w, box_h, 6, fill=False, stroke=True)
        c.setFillColor(colors.HexColor("#64748B"))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(85, box_y + 52, "DATE OF ISSUANCE")
        c.setFillColor(colors.HexColor("#F8FAFC"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(85, box_y + 26, issue_date_str)

        # Badge 2: Official Seal / Stamp (Center)
        seal_x = width / 2.0
        seal_y = box_y + (box_h / 2.0)
        c.setFillColor(colors.HexColor("#065F46"))
        c.circle(seal_x, seal_y, 38, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor("#10B981"))
        c.setLineWidth(2)
        c.circle(seal_x, seal_y, 34, fill=False, stroke=True)
        c.setFillColor(colors.HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(seal_x, seal_y + 12, "VERIFIED")
        c.drawCentredString(seal_x, seal_y, "COMPETENCY")
        c.setFont("Helvetica", 7)
        c.drawCentredString(seal_x, seal_y - 12, "AUTHENTIC")

        # Badge 3: Certificate ID & Security Hash
        c.setFillColor(colors.HexColor("#0F172A"))
        c.roundRect(width - 70 - box_w, box_y, box_w, box_h, 6, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor("#334155"))
        c.roundRect(width - 70 - box_w, box_y, box_w, box_h, 6, fill=False, stroke=True)
        c.setFillColor(colors.HexColor("#64748B"))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(width - 70 - box_w + 15, box_y + 52, "CERTIFICATE ID")
        c.setFillColor(colors.HexColor("#38BDF8"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(width - 70 - box_w + 15, box_y + 26, certificate_id)

        # -----------------------------------------------------------
        # 6. Verification Footer
        # -----------------------------------------------------------
        hash_preview = (verification_hash[:24] + "...") if verification_hash else "SHA256-VERIFIED"
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2.0, 60, f"Online Verification ID: {certificate_id}  •  Security Hash: {hash_preview}")
        c.drawCentredString(width / 2.0, 48, "Issued by Linux Commands Learning Assistant — Fully Accredited Virtual Assessment")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
