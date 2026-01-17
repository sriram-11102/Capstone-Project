"""
Real-Time File Monitor (Watcher)
--------------------------------
This script acts as the entry point for the "Production Mode" of the system.
It actively monitors the 'input/' directory for new files, passes them to the
ValidationEngine, and moves them to 'processed/' or 'rejected/' based on the result.

Author: Sriram
Last Updated: Jan 2026
"""

import time
import os
import shutil
from src.validator.engine import ValidationEngine
from src.validator.logger import logger

# --- Configuration ---
INPUT_DIR = "input"
PROCESSED_DIR = "processed"
REJECTED_DIR = "rejected"
POLL_INTERVAL = 1  # Seconds to wait between directory scans

def ensure_dirs():
    """Ensure that all necessary runtime directories exist."""
    print(f"[System] Verifying directory structure...")
    for d in [INPUT_DIR, PROCESSED_DIR, REJECTED_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"[System] Created directory: {d}")

def move_file(filepath, dest_dir):
    """
    Moves a processed file to the destination directory.
    Handles name collisions by appending a timestamp.
    """
    filename = os.path.basename(filepath)
    dest_path = os.path.join(dest_dir, filename)
    
    # If file already exists in destination, rename the new one
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(filename)
        timestamp = time.strftime("%Y%m%d%H%M%S")
        dest_path = os.path.join(dest_dir, f"{base}_{timestamp}{ext}")
        
    try:
        shutil.move(filepath, dest_path)
        logger.info(f"Moved {filename} -> {dest_path}")
    except Exception as e:
        logger.error(f"Failed to move {filename}: {e}")

def watch():
    """Main Monitoring Loop"""
    ensure_dirs()
    print(f"\n=== VALIDATOR WATCHER ACTIVE ===")
    print(f"[*] Monitoring Directory: {os.path.abspath(INPUT_DIR)}")
    print(f"[*] Polling Interval:     {POLL_INTERVAL} seconds")
    print(f"[*] Press Ctrl+C to stop.\n")
    
    # Initialize Engine once (it will reload config internally per file)
    engine = ValidationEngine("config.json")
    
    while True:
        try:
            # 1. Scan for files
            files = [f for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f))]
            
            for filename in files:
                filepath = os.path.join(INPUT_DIR, filename)
                
                # 2. Process
                # engine.process_file returns:
                # True  -> Validation Passed
                # False -> Validation Failed
                # None  -> System Error / No Route Found
                result = engine.process_file(os.path.abspath(filepath))
                
                # 3. Route Output
                if result is True:
                    move_file(filepath, PROCESSED_DIR)
                elif result is False:
                    move_file(filepath, REJECTED_DIR)
                else:
                    # If unprocessable (e.g., config error), move to rejected to prevent infinite loop
                    logger.warning(f"File {filename} skipped or unprocessable. Moving to rejected.")
                    move_file(filepath, REJECTED_DIR)
            
            # 4. Wait
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n[System] Stopping Watcher...")
            break
        except Exception as e:
            logger.error(f"Watcher loop critical error: {e}")
            time.sleep(POLL_INTERVAL) # Prevent rapid error looping

if __name__ == "__main__":
    watch()
