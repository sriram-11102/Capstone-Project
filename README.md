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

### 1. One-Click Launch
Double-click **`run.bat`** (Windows) to:
1.  Start the API & Dashboard.
2.  Start the **File Watcher**.
3.  Open the Dashboard.

### 2. How to Use
1.  Drop your data files (`.txt` or `.csv`) into the **`input/`** folder.
2.  The system automatically detects, processes, and validates them.
3.  **Valid files** move to `processed/`.
4.  **Invalid files** move to `rejected/` (and trigger alerts).

### 3. Manual Execution
**Start Backend:**
```bash
uvicorn src.validator.api:app --reload
```
**Start Watcher:**
```bash
python watcher.py
```

## Project Structure
*   `src/validator/`: Core logic (Engine, Rules, Router, Alerter).
*   `src/validator/static/`: Premium V5 Dashboard.
*   `watcher.py`: Real-time file monitor.
*   `run.bat`: Launcher script.
*   `config.json`: Production rules configuration.

## Features
*   **Real-Time Monitoring**: Watches `input/` folder for new files.
*   **Automatic Routing**: Sorts files into `processed/` or `rejected/` based on validation.
*   **Command Center UI**: Live tracking of processing status.
*   **Smart Alerts**: Email & ServiceNow integration.
*   **Custom DSL**: Define business rules in `config.json`.

## Configuration
Set environment variables for alerting:
- `SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`
- `SNOW_INSTANCE_URL`, `SNOW_USER`, `SNOW_PASSWORD`
