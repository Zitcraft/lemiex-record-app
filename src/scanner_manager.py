"""
Scanner Manager Module - Handles barcode scanner operations
Manages COM port scanning, barcode reading, and QR code parsing
"""

import serial
import serial.tools.list_ports
import re
import threading
import time
from typing import List, Optional, Callable
from pathlib import Path
import yaml
from .logger import setup_logger

logger = setup_logger("ScannerManager")


class ScannerManager:
    """Manages barcode scanner operations via serial port"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Scanner Manager
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.scanner_config = self.config['scanner']
        
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_listening = False
        self.listen_thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None
        
        # Compile regex pattern for QR code parsing
        self.qr_pattern = re.compile(self.scanner_config['qr_url_pattern'])
        
        logger.info("ScannerManager initialized")
    
    def list_available_ports(self) -> List[tuple]:
        """
        List all available COM ports
        
        Returns:
            List of tuples (port, description, hwid)
        """
        ports = serial.tools.list_ports.comports()
        available_ports = []
        
        logger.info("Scanning for serial ports")
        
        for port in ports:
            available_ports.append((port.device, port.description, port.hwid))
            logger.info(f"Found port: {port.device} - {port.description}")
        
        if not available_ports:
            logger.warning("No serial ports found")
        
        return available_ports
    
    def connect(self, port: str) -> bool:
        """
        Connect to scanner on specified COM port
        
        Args:
            port: COM port name (e.g., 'COM3')
            
        Returns:
            True if connected successfully
        """
        try:
            if self.is_connected:
                self.disconnect()
            
            logger.info(f"Connecting to scanner on {port}")
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.scanner_config['baud_rate'],
                timeout=self.scanner_config['timeout'],
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            if self.serial_port.is_open:
                self.is_connected = True
                logger.info(f"Connected to scanner on {port}")
                return True
            else:
                logger.error(f"Failed to open port {port}")
                return False
                
        except serial.SerialException as e:
            logger.error(f"Serial exception: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to scanner: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from scanner"""
        self.stop_listening()
        
        if self.serial_port is not None and self.serial_port.is_open:
            self.serial_port.close()
            logger.info("Disconnected from scanner")
        
        self.is_connected = False
        self.serial_port = None
    
    def read_once(self) -> Optional[str]:
        """
        Read one barcode scan
        
        Returns:
            Scanned data as string or None
        """
        if not self.is_connected or self.serial_port is None:
            logger.warning("Scanner not connected")
            return None
        
        try:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.readline()
                decoded = data.decode('utf-8', errors='ignore').strip()
                logger.debug(f"Raw scan data: {decoded}")
                return decoded
            return None
            
        except Exception as e:
            logger.error(f"Error reading from scanner: {str(e)}")
            return None
    
    def parse_order_id(self, scanned_data: str) -> Optional[str]:
        """
        Parse order ID from scanned QR code data
        
        Args:
            scanned_data: Raw scanned data
            
        Returns:
            Extracted order ID or None
        """
        if not scanned_data:
            return None
        
        # Try to match URL pattern
        match = self.qr_pattern.search(scanned_data)
        if match:
            order_id = match.group(1)
            logger.info(f"Parsed order ID: {order_id} from {scanned_data}")
            return order_id
        
        # If no match, check if it's already just a number
        if scanned_data.isdigit():
            logger.info(f"Direct order ID: {scanned_data}")
            return scanned_data
        
        logger.warning(f"Could not parse order ID from: {scanned_data}")
        return None
    
    def start_listening(self, callback: Callable[[str], None]):
        """
        Start listening for scanner input in background thread
        
        Args:
            callback: Function to call with parsed order ID
        """
        if not self.is_connected:
            logger.error("Cannot start listening - scanner not connected")
            return
        
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        self.callback = callback
        self.is_listening = True
        
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        
        logger.info("Started listening for scanner input")
    
    def stop_listening(self):
        """Stop listening for scanner input"""
        if self.is_listening:
            self.is_listening = False
            
            if self.listen_thread is not None:
                self.listen_thread.join(timeout=2)
                self.listen_thread = None
            
            logger.info("Stopped listening for scanner input")
    
    def _listen_loop(self):
        """Background thread loop for listening to scanner"""
        logger.debug("Listen loop started")
        
        while self.is_listening:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline()
                    decoded = data.decode('utf-8', errors='ignore').strip()
                    
                    if decoded:
                        logger.debug(f"Scanned: {decoded}")
                        order_id = self.parse_order_id(decoded)
                        
                        if order_id and self.callback:
                            self.callback(order_id)
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"Error in listen loop: {str(e)}")
                time.sleep(1)  # Longer delay on error
        
        logger.debug("Listen loop ended")
    
    def auto_detect_scanner(self) -> Optional[str]:
        """
        Attempt to auto-detect scanner port
        
        Returns:
            Port name if found, None otherwise
        """
        logger.info("Auto-detecting scanner...")
        
        ports = self.list_available_ports()
        
        # Check if default port exists
        default_port = self.scanner_config['default_port']
        for port, desc, hwid in ports:
            if port == default_port:
                logger.info(f"Found default port: {default_port}")
                return default_port
        
        # Try to find USB scanner (common keywords in description)
        scanner_keywords = ['scanner', 'barcode', 'usb serial', 'ch340', 'cp210', 'ftdi']
        
        for port, desc, hwid in ports:
            desc_lower = desc.lower()
            if any(keyword in desc_lower for keyword in scanner_keywords):
                logger.info(f"Auto-detected scanner on {port}: {desc}")
                return port
        
        # If only one port, assume it's the scanner
        if len(ports) == 1:
            port = ports[0][0]
            logger.info(f"Only one port available, selecting: {port}")
            return port
        
        logger.warning("Could not auto-detect scanner")
        return None
    
    def __del__(self):
        """Cleanup resources"""
        self.disconnect()


if __name__ == "__main__":
    # Test scanner manager
    manager = ScannerManager()
    
    # List ports
    ports = manager.list_available_ports()
    print(f"\nFound {len(ports)} serial port(s):")
    for port, desc, hwid in ports:
        print(f"  {port}: {desc}")
    
    # Test QR parsing
    test_urls = [
        "https://lemiex.us/qr/6079",
        "6079",
        "https://lemiex.us/qr/12345",
        "invalid_data"
    ]
    
    print("\nTesting QR code parsing:")
    for url in test_urls:
        order_id = manager.parse_order_id(url)
        print(f"  {url} -> {order_id}")
