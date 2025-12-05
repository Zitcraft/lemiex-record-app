"""
Generate QR codes for Lemiex Record App
Creates 3 QR codes:
1. USB-COM.svg - QR for USB-COM setup instructions
2. Factory-Default.svg - QR for factory default settings
3. app-identifier.svg - QR for app identification (makes app flash when scanned)
"""
import qrcode
import qrcode.image.svg
from pathlib import Path

def generate_qr_code(data: str, filename: str, output_dir: Path):
    """
    Generate QR code as SVG
    
    Args:
        data: Data to encode in QR code
        filename: Output filename (without extension)
        output_dir: Output directory
    """
    # Create QR code factory
    factory = qrcode.image.svg.SvgPathImage
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,  # Size 1-40
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Generate SVG image
    img = qr.make_image(image_factory=factory, fill_color="black", back_color="white")
    
    # Save to file
    output_path = output_dir / f"{filename}.svg"
    img.save(str(output_path))
    print(f"✓ Generated: {output_path}")
    
    return output_path


def main():
    # Create output directory
    output_dir = Path(__file__).parent / "qr_codes"
    output_dir.mkdir(exist_ok=True)
    
    print("Generating QR codes for Lemiex Record App...")
    print("=" * 60)
    
    # 1. USB-COM QR (links to documentation)
    generate_qr_code(
        data="USB-COM-SETUP",
        filename="USB-COM",
        output_dir=output_dir
    )
    
    # 2. Factory Default QR (reset command)
    generate_qr_code(
        data="FACTORY-DEFAULT",
        filename="Factory-Default",
        output_dir=output_dir
    )
    
    # 3. App Identifier QR (unique identifier for this app)
    generate_qr_code(
        data="LEMIEX-RECORD-APP-IDENTIFIER-COM3",
        filename="app-identifier",
        output_dir=output_dir
    )
    
    print("=" * 60)
    print("✓ All QR codes generated successfully!")
    print(f"✓ Location: {output_dir}")


if __name__ == "__main__":
    main()
