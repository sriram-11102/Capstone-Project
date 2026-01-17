from src.validator.config_manager import ConfigManager
from src.validator.engine import ValidationEngine
from src.validator.data_generator import DataGenerator
import os
import time

def run_stress_test():
    print("=== FINANCIAL DATA STRESS TEST (DYNAMIC) ===\n")
    
    config_file = "financial_stress_config.json"
    if os.path.exists(config_file):
        os.remove(config_file)
        
    cm = ConfigManager(config_file)
    
    # Define Financial Rules
    print("[Config] Setting up Financial Rules")
    cm.add_ruleset("financial_rules", [
        "1C REQUIRED",
        "1C IS ALPHANUM",
        "1C STARTS_WITH \"TXN\"",
        "3C MATCHES \"(USD|EUR|GBP|INR|JPY)\"",
        "4C IS NUMERIC",
        "4C > 0"
    ])
    # Router matches timestamped files: Financial-Valid-2024....txt
    cm.add_route(r"Financial-.*\.txt", "financial_rules")
    
    # Inject System Config (Alerts)
    system_config = {
        "email_recipients": ["202117B3762@wilp.bits-pilani.ac.in", "sriramramanathan9544@gmail.com"],
        "smtp_config": {
            "server": "smtp.gmail.com",
            "port": 587,
            "sender_email": "sriramramanathan9544@gmail.com",
            "sender_password": "fheq hgrz ipfx yewp"
        },
        "servicenow": {
            "instance_url": "https://dev275610.service-now.com/",
            "username": "admin",
            "password": "a1zu9UsSJ%M@"
        }
    }
    cm.set_system_config(system_config)

    # 2. Generate DYNAMIC Data
    gen = DataGenerator(output_dir=".")
    
    # Valid Batch (5000 rows)
    file_valid = gen.generate_financial_batch(5000, valid=True)
    
    # Invalid Batch (5000 rows)
    file_invalid = gen.generate_financial_batch(5000, valid=False)

    # 3. Run Engine
    print("\n[Execution] Starting Validation Engine...")
    engine = ValidationEngine(config_file)
    
    t0 = time.time()
    engine.process_file(os.path.abspath(file_valid))
    t1 = time.time()
    print(f"Processed Valid File {file_valid} in {t1-t0:.2f}s")
    
    engine.process_file(os.path.abspath(file_invalid))
    t2 = time.time()
    print(f"Processed Invalid File {file_invalid} in {t2-t1:.2f}s")
    
    # Cleanup config only (keep data to show dynamic names)
    if os.path.exists(config_file):
        os.remove(config_file)

if __name__ == "__main__":
    run_stress_test()
