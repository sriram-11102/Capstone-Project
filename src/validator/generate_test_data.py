"""
Large Dataset Generator
-----------------------
Utility script to generate synthetic test data for performance validation.
Creates files with 75 columns and 200 rows, mixing strict financial data with random filler.

Columns:
  1C: Transaction ID (Startswith TXN)
  2C: Client Name
  3C: Currency (USD, EUR, GBP, INR, JPY)
  4C: Amount (Numeric > 0)
  5C: Account Type (Savings, Current, Corporate)
  6C: Risk Score (0-100)
  7C-75C: Filler Strings
"""

import csv
import random
import os
import time

OUTPUT_DIR = "input"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_row(is_valid, num_columns=75):
    """
    Generates a single row of data.
    If is_valid is False, injects random errors into the strict fields.
    """
    row = []
    
    # --- Column 1: Transaction ID ---
    # Rule: Must start with "TXN"
    if is_valid:
        row.append(f"TXN{random.randint(100000,999999)}")
    else:
        # 50% chance to fail this specific rule
        if random.random() < 0.5:
            row.append("INVALID_ID")
        else:
            row.append(f"TXN{random.randint(100000,999999)}")
            
    # --- Column 2: Client Name ---
    # Rule: No strict validation, just needs to be present
    row.append(f"Client_{random.randint(1,100)}")
    
    # --- Column 3: Currency ---
    # Rule: Must match standard ISO codes
    currencies = ["USD", "EUR", "GBP", "INR", "JPY"]
    if is_valid:
        row.append(random.choice(currencies))
    else:
        # Inject invalid currency code
        if random.random() < 0.5:
            row.append("BITCOIN") 
        else:
            row.append(random.choice(currencies))
            
    # --- Column 4: Amount ---
    # Rule: Must be a positive number
    if is_valid:
        row.append(round(random.uniform(10, 10000), 2))
    else:
        # Inject negative amount
        if random.random() < 0.5:
            row.append(-100.50)
        else:
            row.append(round(random.uniform(10, 10000), 2))
            
    # --- Column 5: Account Type ---
    # Rule: Must be Savings, Current, or Corporate
    acct_types = ["Savings", "Current", "Corporate"]
    if is_valid:
        row.append(random.choice(acct_types))
    else:
        if random.random() < 0.3:
            row.append("Unknown_Type")
        else:
            row.append(random.choice(acct_types))

    # --- Column 6: Risk Score ---
    # Rule: 0 to 100
    if is_valid:
        row.append(random.randint(0, 100))
    else:
        if random.random() < 0.3:
            row.append(999) # Invalid score
        else:
            row.append(random.randint(0, 100))

    # --- Columns 7-75: Filler Data ---
    # Used to test system performance with wide files
    for i in range(7, num_columns + 1):
        row.append(f"Val_{i}_{random.randint(100,999)}")
        
    return row

def generate_files():
    """Generates one Valid and one Invalid file in the output directory."""
    print(f"[Generator] Starting generation for target directory: {OUTPUT_DIR}")
    ensure_dir(OUTPUT_DIR)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    # 1. Generate 5 Valid Files
    for i in range(1, 6):
        fname_valid = f"Financial-Large-Valid-{timestamp}-{i}.txt"
        fpath_valid = os.path.join(OUTPUT_DIR, fname_valid)
        
        with open(fpath_valid, "w", newline="") as f:
            writer = csv.writer(f)
            for _ in range(200): # 200 Rows
                writer.writerow(generate_row(is_valid=True))
        print(f"[Generator] Created Valid File:   {fname_valid}")

    # 2. Generate 15 Invalid Files
    for i in range(1, 16):
        fname_invalid = f"Financial-Large-Invalid-{timestamp}-{i}.txt"
        fpath_invalid = os.path.join(OUTPUT_DIR, fname_invalid)
        
        with open(fpath_invalid, "w", newline="") as f:
            writer = csv.writer(f)
            for _ in range(200): # 200 Rows
                writer.writerow(generate_row(is_valid=False))
        print(f"[Generator] Created Invalid File: {fname_invalid}")

if __name__ == "__main__":
    generate_files()
