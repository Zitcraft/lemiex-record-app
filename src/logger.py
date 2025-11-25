"""
Logger Module - Centralized logging configuration
Provides logging functionality with file rotation and formatting
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import yaml


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def setup_logger(name: str = "LemiexRecordApp") -> logging.Logger:
    """
    Setup and configure logger with rotating file handler
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    config = load_config()
    log_config = config['logging']
    
    # Create logs directory if not exists
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_config['level']))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(
        log_config['format'],
        datefmt=log_config['date_format']
    )
    
    # File handler with rotation
    log_file = log_dir / "app.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=log_config['max_bytes'],
        backupCount=log_config['backup_count'],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()


if __name__ == "__main__":
    # Test logging
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
