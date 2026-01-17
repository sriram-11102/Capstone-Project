"""
Central Logger
--------------
Provides a consistent logging configuration across the application.
Writes to both Console (Stdout) and File (validator.log).
"""

import logging
import sys
import os

def setup_logger(name: str = "validator", log_file: str = "validator.log", level=logging.INFO):
    """
    Configures and returns a singleton-like logger.
    """
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # 1. File Handler (Rotates logs? No, simple append for now)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # 2. Console Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)
    
    # Check handlers to avoid duplicate lines if called multiple times
    if not logger_instance.handlers:
        logger_instance.addHandler(file_handler)
        logger_instance.addHandler(stream_handler)
        
    return logger_instance

# Global logger instance used by other modules
logger = setup_logger()
