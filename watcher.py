import time
import os
import shutil
from src.validator.engine import ValidationEngine
from src.validator.logger import logger

INPUT_DIR = "input"
PROCESSED_DIR = "processed"
REJECTED_DIR = "rejected"
POLL_INTERVAL = 1

def ensure_dirs():
    for d in [INPUT_DIR, PROCESSED_DIR, REJECTED_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def move_file(filepath, dest_dir):
    filename = os.path.basename(filepath)
    dest_path = os.path.join(dest_dir, filename)
    
    # Handle duplicates
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
    ensure_dirs()
    print(f"=== VALIDATOR WATCHER ACTIVE ===")
    print(f"Monitoring: {os.path.abspath(INPUT_DIR)}")
    print(f"Interval:   {POLL_INTERVAL}s")
    
    engine = ValidationEngine("config.json")
    
    while True:
        try:
            files = [f for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f))]
            
            for filename in files:
                filepath = os.path.join(INPUT_DIR, filename)
                
                # Verify
                result = engine.process_file(os.path.abspath(filepath))
                
                # Move
                if result is True:
                    move_file(filepath, PROCESSED_DIR)
                elif result is False:
                    move_file(filepath, REJECTED_DIR)
                else:
                    # Result None means file error or empty or no route
                    # Move to rejected to avoid endless loop processing same file
                    logger.warning(f"File {filename} skipped or unprocessable. Moving to rejected.")
                    move_file(filepath, REJECTED_DIR)
                    
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nStopping Watcher...")
            break
        except Exception as e:
            logger.error(f"Watcher loop error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    watch()
