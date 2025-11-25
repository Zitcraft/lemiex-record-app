"""
Lemiex Record App - Main Entry Point
Webcam recording application with barcode scanner integration
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.main_window import run_app
from src.logger import setup_logger

logger = setup_logger("Main")


def main():
    """Main application entry point"""
    try:
        logger.info("=" * 50)
        logger.info("Lemiex Record App Starting")
        logger.info("=" * 50)
        
        run_app()
        
        logger.info("Application closed normally")
        
    except Exception as e:
        logger.critical(f"Application crashed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
