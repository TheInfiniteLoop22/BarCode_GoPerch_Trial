from fastapi import FastAPI
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

app = FastAPI()

BARCODE_DIR = "barcodes"
PDF_DIR = "pdfs"

os.makedirs(BARCODE_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


# ----------------------------
# 1. Generate a barcode image
# ----------------------------
def generate_barcode_image(barcode_text: str) -> str:
    barcode = Code128(barcode_text, writer=ImageWriter())

    # Windows-safe filename
    safe_filename = (
        barcode_text
        .replace("|", "_")
        .replace(":", "_")
    )

    filename = barcode.save(
        os.path.join(BARCODE_DIR, safe_filename)
    )

    return filename


# ----------------------------
# 2. Generate PDF labels
# ----------------------------
def generate_labels_pdf(job: dict) -> str:
    pdf_path = os.path.join(PDF_DIR, f"job_{job['job_id']}_labels.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)

    width, height = A4

    for item in job["items"]:
        # 🔥 UPDATED BARCODE FORMAT (NO V1)
        barcode_text = f"J:{job['job_id']}|P:{item['product_id']}"
        barcode_image = generate_barcode_image(barcode_text)

        for i in range(item["qty"]):
            c.drawImage(barcode_image, 50, height - 150, width=300, height=80)

            c.drawString(50, height - 170, f"Job ID: {job['job_id']}")
            c.drawString(50, height - 185, f"Product: {item['product_name']}")
            c.drawString(50, height - 200, f"Product ID: {item['product_id']}")
            c.drawString(50, height - 215, f"Unit: {i + 1} of {item['qty']}")

            c.showPage()

    c.save()
    return pdf_path


# ----------------------------
# 3. API Endpoint
# ----------------------------
@app.get("/generate-demo-job")
def generate_demo_job():
    demo_job = {
        "job_id": 102,
        "items": [
            {"product_id": 455, "product_name": "Maple Tree", "qty": 3},
            {"product_id": 233, "product_name": "Clay Vase", "qty": 2}
        ]
    }

    pdf_path = generate_labels_pdf(demo_job)

    return {
        "message": "Barcodes and PDF generated successfully",
        "pdf": pdf_path
    }
