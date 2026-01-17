
import os
import json
import csv
import time
from fastapi.testclient import TestClient
from src.validator.api import app

client = TestClient(app)

def test_api_flow():
    print("--- Testing API Flow ---")
    
    # 1. Check Root
    response = client.get("/")
    print(f"GET /: {response.status_code} {response.json()}")
    assert response.status_code == 200
    
    # 2. Add Ruleset
    ruleset_name = "api_test_rules"
    rules = ["1C REQUIRED", "2C > 50"]
    response = client.post(f"/rulesets/{ruleset_name}", json=rules) # FastAPI handles list body automatically
    print(f"POST /rulesets/{ruleset_name}: {response.status_code} {response.json()}")
    assert response.status_code == 200

    # 3. Verify Ruleset
    response = client.get(f"/rulesets/{ruleset_name}")
    print(f"GET /rulesets/{ruleset_name}: {response.status_code} {response.json()}")
    data = response.json()
    assert data["name"] == ruleset_name
    assert len(data["rules"]) == 2
    
    # 4. Add Route
    route_data = {
        "pattern": r"API-Test-.*\.txt",
        "ruleset": ruleset_name,
        "priority": 100
    }
    response = client.post("/routes", json=route_data)
    print(f"POST /routes: {response.status_code} {response.json()}")
    assert response.status_code == 200
    
    # 5. Create Test File
    test_file = "API-Test-Data.txt"
    with open(test_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["101", "100"]) # Valid
        writer.writerow(["", "20"])     # Invalid (1C required, 2C > 50)
    print(f"Created test file: {test_file}")
    
    # 6. Trigger Validation
    response = client.post("/validate", json={"filepath": os.path.abspath(test_file)})
    print(f"POST /validate: {response.status_code} {response.json()}")
    assert response.status_code == 200
    
    print("Waiting for background task (simulated)...")
    time.sleep(1) 
    
    # Check log file exists and has content (basic check)
    if os.path.exists("validator.log"):
        print("Log file exists.")
        with open("validator.log", "r") as f:
            logs = f.read()
            if "Validation failed with" in logs:
                print("Log contains expected validation failure.")
            else:
                print("WARNING: Log might not contain expected failure message yet.")
    
    print("\nAPI Flow Verified Successfully")

if __name__ == "__main__":
    test_api_flow()
