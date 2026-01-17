# Real-Time File Monitoring System
**Capstone Project - Sriram Ramanathan (202117B3762)**

A dynamic, rule-driven file validation system designed to automate compliance monitoring for financial and operational files.

## Features
- **Custom DSL**: Define rules like `4C = 1C+2C`, `51C IS ALPHANUM`.
- **Pattern-Based Routing**: Automatically routes files (e.g., `Accounting-*.txt`) to specific rulesets.
- **Real-Time Validation**: Validates files instantly upon processing.
- **Alerting**: Integrates with **Email** and **ServiceNow** for incident management.
- **Management API**: REST API for managing rules and routes on the fly.

## Quick Start 🚀

### 1. One-Click Launch (Recommended)
Double-click **`run.bat`** (Windows) to automatically:
1.  Start the API & Dashboard.
2.  Launch the Operations Dashboard in your browser.
3.  Run the **Financial Stress Test** simulation.

### 2. Manual Execution
**Start the Dashboard/API:**
```bash
uvicorn src.validator.api:app --reload
```
*Access: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)*

**Run Validation Workflow:**
```bash
python stress_test.py
```
*This will generate unique timestamped financial data and validate it in real-time.*

## Project Structure
*   `src/validator/`: Core logic (Engine, Rules, Router, Alerter).
*   `src/validator/static/`: Premium V5 Dashboard (HTML/CSS/JS).
*   `src/validator/data_generator.py`: Dynamic test data generator.
*   `stress_test.py`: Main simulation script.
*   `run.bat`: Launcher script.
*   `config.json`: Production rules configuration.

## Features
*   **Dynamic Data**: Generates fresh, randomized financial datasets on every run.
*   **Real-Time Dashboard**: "Command Center" UI with live file tracking, charts, and incident history.
*   **Smart Alerts**: Intelligent email and ServiceNow integration.
*   **Custom DSL**: Define business rules in simple English (e.g., `1C REQUIRED`).

## Configuration
Set environment variables for alerting:
- `SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`
- `SNOW_INSTANCE_URL`, `SNOW_USER`, `SNOW_PASSWORD`
