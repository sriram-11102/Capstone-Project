import csv
import random
import os
import time

OUTPUT_DIR = "input"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_row(is_valid, num_columns=75):
    # Rules:
    # 1C: starts with TXN
    # 3C: USD|EUR|GBP|INR|JPY
    # 4C: Numeric > 0
    
    row = []
    
    # Col 1: ID
    if is_valid:
        row.append(f"TXN{random.randint(100000,999999)}")
    else:
        # Invalid: 50% chance to fail this rule
        if random.random() < 0.5:
            row.append("INVALID_ID")
        else:
            row.append(f"TXN{random.randint(100000,999999)}")
            
    # Col 2: Name
    row.append(f"Client_{random.randint(1,100)}")
    
    # Col 3: Currency
    currencies = ["USD", "EUR", "GBP", "INR", "JPY"]
    if is_valid:
        row.append(random.choice(currencies))
    else:
        # Invalid: If Col 1 was valid, force this to fail (or just fail randomly)
        # To ensure "Invalid" file is actually invalid, we force failure on at least one field if we haven't yet.
        # Simple approach: If is_valid=False, just randomize failure.
        if random.random() < 0.5:
            row.append("BITCOIN") 
        else:
            row.append(random.choice(currencies))
            
    # Col 4: Amount
    if is_valid:
        row.append(round(random.uniform(10, 10000), 2))
    else:
        if random.random() < 0.5:
            row.append(-100.50)
        else:
            row.append(round(random.uniform(10, 10000), 2))
            
    # Col 5: Account Type
    acct_types = ["Savings", "Current", "Corporate"]
    if is_valid:
        row.append(random.choice(acct_types))
    else:
        if random.random() < 0.3:
            row.append("Unknown_Type") # Invalid account
        else:
            row.append(random.choice(acct_types))

    # Col 6: Risk Score (0-100)
    if is_valid:
        row.append(random.randint(0, 100))
    else:
        if random.random() < 0.3:
            row.append(999) # Invalid score > 100
        else:
            row.append(random.randint(0, 100))

    # Col 7 to 75: Filler Data
    for i in range(7, num_columns + 1):
        row.append(f"Val_{i}_{random.randint(100,999)}")
        
    # Ensure invalid file has at least one error if purely random choices accidentally made it valid
    if not is_valid:
        # Force Col 4 to be negative just in case
        row[3] = -999.99
        
    return row

def generate_files():
    ensure_dir(OUTPUT_DIR)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    # 1. Valid File
    fname_valid = f"Financial-Large-Valid-{timestamp}.txt"
    fpath_valid = os.path.join(OUTPUT_DIR, fname_valid)
    
    with open(fpath_valid, "w", newline="") as f:
        writer = csv.writer(f)
        for _ in range(200):
            writer.writerow(generate_row(is_valid=True))
            
    print(f"[Generator] Created Valid File: {fname_valid} (200 rows, 75 cols)")

    # 2. Invalid File
    fname_invalid = f"Financial-Large-Invalid-{timestamp}.txt"
    fpath_invalid = os.path.join(OUTPUT_DIR, fname_invalid)
    
    with open(fpath_invalid, "w", newline="") as f:
        writer = csv.writer(f)
        for _ in range(200):
            writer.writerow(generate_row(is_valid=False))
            
    print(f"[Generator] Created Invalid File: {fname_invalid} (200 rows, 75 cols)")

if __name__ == "__main__":
    generate_files()
