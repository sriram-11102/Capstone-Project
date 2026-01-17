from src.validator.config_manager import ConfigManager
from src.validator.engine import ValidationEngine
import csv
import os
import time
import random

def generate_wide_data(filename, rows, cols, valid=True):
    print(f"Generatng {filename} with {rows} rows and {cols} columns...")
    start_time = time.time()
    
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for i in range(rows):
            row = []
            for c in range(cols):
                # Generate varied data
                if c == 0:
                    row.append(f"ID_{i}") # 1C: ID
                elif c == 99: 
                    # 100C: Random int
                    row.append(random.randint(100, 1000))
                elif c == 149:
                    # 150C: Status (Last col for 150-col file)
                    if valid:
                        row.append("ACTIVE")
                    else:
                        # Inject error in last row
                        row.append("ACTIVE" if i < rows-1 else "INVALID")
                else:
                    # Random numeric filler
                    row.append(c * 10 + i)
            writer.writerow(row)
            
    print(f"Generated in {time.time() - start_time:.2f}s")

def run_stress_test():
    print("=== HIGH DIMENSIONALITY STRESS TEST ===\n")
    
    config_file = "stress_config.json"
    if os.path.exists(config_file):
        os.remove(config_file)
        
    cm = ConfigManager(config_file)
    
    # --- SCENARIO 1: Deep Column Check ---
    # File: 150 Columns
    # Rules: Check 150th column type and value
    print("[Config] Scenario 1: Checking Column 150 (Deep Column)")
    cm.add_ruleset("deep_col_rules", [
        "150C REQUIRED", 
        "150C IS ALPHANUM",
        "150C = \"ACTIVE\"" 
    ])
    cm.add_route(r"WideData-150-.*\.txt", "deep_col_rules")
    
    # --- SCENARIO 2: Cross-Column Arithmetic ---
    # File: 120 Columns
    # Rules: Check if Col 20 > Col 10 (Simulated consistency check)
    # Note: 50C > 40C is now supported by our DSL update
    print("[Config] Scenario 2: Relative checks (50C > 40C)")
    cm.add_ruleset("relative_rules", [
        "50C > 40C",
        "1C STARTS_WITH \"ID_\""
    ])
    cm.add_route(r"WideData-Rel-.*\.txt", "relative_rules")

    # Generate Data
    file_150 = "WideData-150-Valid.txt"
    # 2000 rows, 150 columns
    generate_wide_data(file_150, 2000, 150, valid=True)
    
    file_rel = "WideData-Rel-Mixed.txt"
    # 2000 rows, 120 columns
    generate_wide_data(file_rel, 2000, 120, valid=True)

    # Run Engine
    print("\n[Execution] Starting Validation Engine...")
    engine = ValidationEngine(config_file)
    
    t0 = time.time()
    engine.process_file(os.path.abspath(file_150))
    t1 = time.time()
    print(f"Processed 150-col file in {t1-t0:.2f}s")
    
    engine.process_file(os.path.abspath(file_rel))
    t2 = time.time()
    print(f"Processed 120-col file in {t2-t1:.2f}s")
    
    # Cleanup
    # os.remove(file_150)
    # os.remove(file_rel)
    # os.remove(config_file)

if __name__ == "__main__":
    run_stress_test()
