"""
Print QR Codes to PDF for easy printing and labeling
Creates a PDF with all 3 QR codes with labels
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

def create_qr_pdf():
    """Create a PDF with all 3 QR codes for printing"""
    try:
        from fpdf import FPDF
    except ImportError:
        print("ERROR: fpdf2 is not installed")
        print("Install with: pip install fpdf2")
        return
    
    # Setup PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Title
    pdf.cell(0, 10, "Lemiex Record App - QR Codes", ln=True, align="C")
    pdf.ln(5)
    
    # QR configurations
    qr_configs = [
        {
            "image": "USB-COM.png",
            "title": "USB-COM Setup",
            "description": "Scan for USB-COM configuration",
            "code": "USB-COM-SETUP"
        },
        {
            "image": "Factory-Default.png",
            "title": "Factory Default",
            "description": "Scan to reset settings",
            "code": "FACTORY-DEFAULT"
        },
        {
            "image": "app-identifier.png",
            "title": "App Identifier (COM3)",
            "description": "Scan to identify this app",
            "code": "LEMIEX-RECORD-APP-IDENTIFIER-COM3"
        }
    ]
    
    qr_dir = Path(__file__).parent / "qr_codes"
    
    # Add each QR to PDF
    y_position = 30
    
    for i, qr in enumerate(qr_configs):
        qr_path = qr_dir / qr['image']
        
        if not qr_path.exists():
            print(f"WARNING: {qr_path} not found")
            continue
        
        # Section title
        pdf.set_font("Arial", "B", 14)
        pdf.set_y(y_position)
        pdf.cell(0, 8, f"{i+1}. {qr['title']}", ln=True)
        
        # QR image (centered)
        img_x = (pdf.w - 60) / 2  # Center horizontally
        pdf.image(str(qr_path), x=img_x, y=y_position + 10, w=60, h=60)
        
        # Description
        pdf.set_y(y_position + 72)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, qr['description'], ln=True, align="C")
        
        # QR Code data
        pdf.set_font("Courier", "", 8)
        pdf.cell(0, 5, f"Code: {qr['code']}", ln=True, align="C")
        
        # Separator
        pdf.ln(10)
        y_position += 90
        
        # New page if needed
        if i < len(qr_configs) - 1 and y_position > 200:
            pdf.add_page()
            y_position = 30
    
    # Footer
    pdf.set_y(-30)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, "Lemiex Record App v1.0.0", ln=True, align="C")
    pdf.cell(0, 5, "Print this page and attach QR codes near the workstation", ln=True, align="C")
    
    # Save PDF
    output_path = Path(__file__).parent / "QR_Codes_Print.pdf"
    pdf.output(str(output_path))
    
    print("=" * 60)
    print("✓ QR Codes PDF created successfully!")
    print(f"✓ Location: {output_path}")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Open QR_Codes_Print.pdf")
    print("2. Print the document")
    print("3. Cut out each QR code")
    print("4. Attach to workstation/monitor")
    print("5. Use gun scanner to test")


if __name__ == "__main__":
    create_qr_pdf()
