"""
Convert SVG QR codes to PNG for display in CustomTkinter
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import qrcode

def create_qr_png(data: str, filename: str, output_dir: Path, size: int = 150):
    """
    Generate QR code as PNG
    
    Args:
        data: Data to encode
        filename: Output filename (without extension)
        output_dir: Output directory
        size: Size in pixels (width and height)
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Generate PIL image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to desired size
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Save as PNG
    output_path = output_dir / f"{filename}.png"
    img.save(str(output_path), "PNG")
    print(f"✓ Generated: {output_path}")
    
    return output_path


def main():
    # Create output directory
    output_dir = Path(__file__).parent / "qr_codes"
    output_dir.mkdir(exist_ok=True)
    
    print("Converting QR codes to PNG format...")
    print("=" * 60)
    
    # Generate QR codes as PNG
    qr_configs = [
        {"data": "USB-COM-SETUP", "filename": "USB-COM"},
        {"data": "FACTORY-DEFAULT", "filename": "Factory-Default"},
        {"data": "LEMIEX-RECORD-APP-IDENTIFIER-COM3", "filename": "app-identifier"}
    ]
    
    for config in qr_configs:
        create_qr_png(
            data=config['data'],
            filename=config['filename'],
            output_dir=output_dir,
            size=150  # 150x150 pixels
        )
    
    print("=" * 60)
    print("✓ All QR codes converted to PNG!")
    print(f"✓ Location: {output_dir}")


if __name__ == "__main__":
    main()
