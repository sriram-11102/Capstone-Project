from src.validator.config_manager import ConfigManager
from src.validator.engine import ValidationEngine
import csv
import os

def run_demo():
    print("=== Multi-Scenario Demonstration ===")
    
    # 1. Setup Configuration
    # We will use a separate config file for this demo to not mess up the main one
    config_file = "demo_config.json"
    if os.path.exists(config_file):
        os.remove(config_file)
        
    cm = ConfigManager(config_file)
    
    # --- SCENARIO A: Financial Files ---
    # Rule: Amount > 1000
    print("\n[Config] Setting up Scenario A: Financial Files (Amount > 1000)")
    cm.add_ruleset("financial_rules", ["3C > 1000"])
    cm.add_route(r"Finance-.*\.txt", "financial_rules")
    
    # --- SCENARIO B: Inventory Files ---
    # Rule: Quantity (Column 2) must be positive, Name (Column 1) starts with 'Item'
    print("[Config] Setting up Scenario B: Inventory Files (Qty > 0, Item Name check)")
    cm.add_ruleset("inventory_rules", [
        "2C > 0",
        "1C STARTS_WITH \"Item\""
    ])
    cm.add_route(r"Inventory-.*\.txt", "inventory_rules")
    
    # 2. Create Test Files
    
    # File A (Finance) - Should FAIL (Amount 500 < 1000)
    file_a = "Finance-2024.txt"
    with open(file_a, "w", newline="") as f:
        csv.writer(f).writerow(["TXN001", "VendorX", "500"]) 
    
    # File B (Inventory) - Should PASS
    file_b = "Inventory-Warehouse.txt"
    with open(file_b, "w", newline="") as f:
        csv.writer(f).writerow(["Item-Box", "50"])

    # 3. Run Validation
    engine = ValidationEngine(config_file)
    
    print(f"\n[Execution] Processing {file_a}...")
    engine.process_file(os.path.abspath(file_a))
    
    print(f"\n[Execution] Processing {file_b}...")
    engine.process_file(os.path.abspath(file_b))

if __name__ == "__main__":
    run_demo()
