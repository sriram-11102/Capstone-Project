# Real-Time File Monitoring System
**Capstone Project - Sriram Ramanathan (202117B3762)**

A dynamic, rule-driven file validation system designed to automate compliance monitoring for financial and operational files.

## Features
- **Custom DSL**: Define rules like `4C = 1C+2C`, `51C IS ALPHANUM`.
- **Pattern-Based Routing**: Automatically routes files (e.g., `Accounting-*.txt`) to specific rulesets.
- **Real-Time Validation**: Validates files instantly upon processing.
- **Alerting**: Integrates with **Email** and **ServiceNow** for incident management.
- **Management API**: REST API for managing rules and routes on the fly.

## Structure
- `src/validator/`: Core logic (Parser, Engine, Router, Alerter).
- `verify_system.py`: End-to-end verification script.
- `api.py`: FastAPI entry point.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the API (Backend + Dashboard):
   ```bash
   uvicorn src.validator.api:app --reload
   ```
   **OPEN DASHBOARD:** [http://localhost:8000/dashboard](http://localhost:8000/dashboard)

3. Run Validation Script (To generate activity):
   ```bash
   python stress_test.py
   ```

## Configuration
Set environment variables for alerting:
- `SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`
- `SNOW_INSTANCE_URL`, `SNOW_USER`, `SNOW_PASSWORD`
