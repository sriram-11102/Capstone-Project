
import os
import csv
from src.validator.engine import ValidationEngine
from src.validator.config_manager import ConfigManager

def setup_test_environment():
    """Setup config and sample files"""
    print("Setting up test environment...")
    
    # 1. Create Config
    cm = ConfigManager("test_config.json")
    
    # Define Rules
    cm.add_ruleset("financial_rules", [
        "1C REQUIRED",              # ID
        "2C IS STRING_TYPE",        # Vendor Name
        "3C IS NUMERIC",            # Amount
        "3C > 0",                   # Positive Amount
        "2C STARTS_WITH \"V_\"",    # Vendor starts with V_
    ])
    
    # Define Route
    cm.add_route(
        pattern=r"Accounting-(?P<vendor>\w+)-(?P<geo>\w+)-(?P<period>\d+)\.txt",
        ruleset_name="financial_rules"
    )
    
    # Inject System Config (Alerts)
    system_config = {
        "email_recipients": ["admin@example.com"],
        "smtp_config": {
            "server": "smtp.gmail.com",
            "port": 587,
            "sender_email": "your_email@gmail.com",
            "sender_password": "your_app_password"
        },
        "servicenow": {
            "instance_url": "https://devXXXXX.service-now.com",
            "username": "admin",
            "password": "your_password"
        }
    }
    cm.set_system_config(system_config)
    
    print("Configuration created.")

    # 2. Create Sample Data File (Valid) - 200 Rows
    valid_file = "Accounting-V_Global-US-2023.txt"
    with open(valid_file, "w", newline="") as f:
        writer = csv.writer(f)
        for i in range(1, 201):
            writer.writerow([f"{1000+i}", f"V_Vendor_{i}", f"{100.0 + i}"])
    print(f"Created large valid file: {valid_file} (200 rows)")
    
    # 3. Create Sample Data File (Invalid) - 200 Rows
    # We will inject errors in every 10th row
    invalid_file = "Accounting-BadVendor-US-2023.txt"
    with open(invalid_file, "w", newline="") as f:
        writer = csv.writer(f)
        for i in range(1, 201):
            if i % 10 == 0:
                # Invalid row: Negative amount, Bad Vendor
                writer.writerow([f"{2000+i}", f"Bad_Vendor_{i}", "-50.0"])
            else:
                # Valid row
                writer.writerow([f"{2000+i}", f"V_Vendor_{i}", f"{50.0 + i}"])
                
    print(f"Created large invalid file: {invalid_file} (200 rows, ~20 failures)")
    
    return valid_file, invalid_file

def run_test():
    valid_file, invalid_file = setup_test_environment()
    
    engine = ValidationEngine("test_config.json")
    
    print("\n--- Running Validation on Valid File ---")
    engine.process_file(valid_file)
    
    print("\n--- Running Validation on Invalid File ---")
    engine.process_file(invalid_file)
    
    # Cleanup
    # os.remove(valid_file)
    # os.remove(invalid_file)
    # os.remove("test_config.json")

if __name__ == "__main__":
    run_test()
