"""
Dynamic QR Generator - Creates unique QR code for each app instance
Each time the app starts, a new unique identifier is generated
This allows multiple devices to be identified independently
"""
import uuid
import qrcode
from PIL import Image
from pathlib import Path
from datetime import datetime
import json


class DynamicQRGenerator:
    """Generate and manage dynamic QR codes for app identification"""
    
    def __init__(self, app_dir: Path):
        """
        Initialize QR generator
        
        Args:
            app_dir: Application directory for storing QR and session data
        """
        self.app_dir = app_dir
        self.qr_dir = app_dir / "qr_codes"
        self.qr_dir.mkdir(exist_ok=True)
        
        self.session_file = app_dir / "session.json"
        self.qr_path = self.qr_dir / "app-identifier.png"
        
        # Generate or load session ID
        self.session_id = self._get_or_create_session()
        self.qr_code = self._generate_qr_code()
        
    def _get_or_create_session(self) -> str:
        """
        Get existing session ID or create new one
        Creates a new unique ID each time app starts
        
        Returns:
            Unique session identifier
        """
        # Always create new session ID on startup
        session_id = str(uuid.uuid4())[:8]  # Short 8-char ID
        
        # Get COM port from config if available
        com_port = "UNKNOWN"
        try:
            config_path = self.app_dir.parent / "config" / "config.yaml"
            if config_path.exists():
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    com_port = config.get('scanner', {}).get('default_port', 'UNKNOWN')
        except Exception:
            pass
        
        # Save session info
        session_data = {
            "session_id": session_id,
            "com_port": com_port,
            "timestamp": datetime.now().isoformat(),
            "qr_code": f"LEMIEX-APP-{session_id}"
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"✓ New session created: {session_id} (COM: {com_port})")
        return session_id
    
    def _generate_qr_code(self) -> str:
        """
        Generate QR code with unique session ID
        
        Returns:
            QR code data string
        """
        # Format: LEMIEX-APP-{session_id}
        qr_data = f"LEMIEX-APP-{self.session_id}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        
        # Save to file
        img.save(str(self.qr_path), "PNG")
        print(f"✓ QR code generated: {qr_data}")
        print(f"✓ QR saved to: {self.qr_path}")
        
        return qr_data
    
    def get_qr_code(self) -> str:
        """Get the current QR code data"""
        return self.qr_code
    
    def get_qr_path(self) -> Path:
        """Get path to QR code image"""
        return self.qr_path
    
    def get_session_id(self) -> str:
        """Get current session ID"""
        return self.session_id
    
    def is_my_qr(self, scanned_code: str) -> bool:
        """
        Check if scanned code matches this app's QR
        
        Args:
            scanned_code: The scanned QR code data
            
        Returns:
            True if this is our QR code
        """
        return scanned_code.upper() == self.qr_code.upper()
    
    def get_session_info(self) -> dict:
        """Get session information"""
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


if __name__ == "__main__":
    # Test
    from pathlib import Path
    test_dir = Path(__file__).parent.parent
    
    print("Testing Dynamic QR Generator...")
    print("=" * 60)
    
    generator = DynamicQRGenerator(test_dir)
    
    print("\nSession Info:")
    print(json.dumps(generator.get_session_info(), indent=2))
    
    print("\nQR Code:", generator.get_qr_code())
    print("Session ID:", generator.get_session_id())
    
    # Test matching
    test_codes = [
        generator.get_qr_code(),
        "LEMIEX-APP-12345678",
        "RANDOM-CODE"
    ]
    
    print("\nTesting QR matching:")
    for code in test_codes:
        match = generator.is_my_qr(code)
        print(f"  {code}: {'✓ MATCH' if match else '✗ No match'}")
