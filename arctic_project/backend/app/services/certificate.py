import os
import uuid
from datetime import datetime

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import qrcode

from app.core.config import settings


def generate_certificate_pdf(
    user_full_name: str,
    title: str,
    number: str,
    qr_payload: str,
) -> str:
    os.makedirs(settings.CERTIFICATE_DIR, exist_ok=True)
    file_path = os.path.join(settings.CERTIFICATE_DIR, f"{number}.pdf")

    # QR
    qr_img_path = os.path.join(settings.CERTIFICATE_DIR, f"{number}_qr.png")
    img = qrcode.make(qr_payload)
    img.save(qr_img_path)

    c = canvas.Canvas(file_path, pagesize=landscape(A4))
    w, h = landscape(A4)

    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(w / 2, h - 60, "Удивительная и неизведанная Арктика")

    c.setFont("Helvetica", 18)
    c.drawCentredString(w / 2, h - 100, title)

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w / 2, h / 2 + 20, user_full_name)

    c.setFont("Helvetica", 12)
    c.drawCentredString(w / 2, h / 2 - 20, f"Сертификат № {number}")
    c.drawCentredString(
        w / 2, h / 2 - 40, f"Дата выдачи: {datetime.utcnow().strftime('%d.%m.%Y')}"
    )

    c.drawImage(qr_img_path, w - 60 * mm, 30 * mm, width=40 * mm, height=40 * mm)
    c.showPage()
    c.save()

    return file_path


def make_number(prefix: str = "ARC") -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"