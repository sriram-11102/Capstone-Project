"""
Validation Engine
-----------------
The core coordination module for the system.
Responsibilities:
1. Reload configuration dynamically per file.
2. Route file to appropriate ruleset.
3. Parse rules using DSL Interpreter.
4. Load Data from CSV/TXT.
5. Execute Validation logic.
6. Trigger Alerts on failure.

Author: Sriram
Last Updated: Jan 2026
"""

import csv
import os
from typing import List, Dict, Any
from .config_manager import ConfigManager
from .router import Router
from .dsl import DSLInterpreter
from .alerter import AlertManager
from .logger import logger

class ValidationEngine:
    """
    Main Orchestrator Class.
    Instantiated by the Watcher or API to validate files.
    """
    
    def __init__(self, config_path="config.json"):
        # Initialize Sub-Components
        self.config_manager = ConfigManager(config_path)
        self.router = Router(self.config_manager)
        self.interpreter = DSLInterpreter()
        self.alerter = AlertManager()
        
    def _configure_alerter(self):
        """
        Internal: Reloads alert configuration from the latest config file.
        Ensures that if config.json changes, alerts use new credentials/recipients.
        """
        sys_config = self.config_manager.get_system_config()
        self.alerter.configure(sys_config)

    def load_data(self, filepath: str) -> List[Dict[int, Any]]:
        """
        Reads input file (CSV/TXT) and converts it to a structured format.
        
        Format:
        Row 1 -> {1: "ValueCol1", 2: "ValueCol2", ...}
        
        Supports automatic type inference (int/float) to simplify validation logic.
        """
        data = []
        try:
            with open(filepath, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    # Map row items to 1-based column indices (1C, 2C...)
                    item = {}
                    for i, val in enumerate(row, 1):
                        val = val.strip()
                        # Auto-detect numeric types
                        try:
                            item[i] = int(val)
                        except ValueError:
                            try:
                                item[i] = float(val)
                            except ValueError:
                                item[i] = val # Keep as string
                    data.append(item)
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {e}")
        return data

    def process_file(self, filepath: str):
        """
        Main entry point for verifying a single file.
        
        Returns:
            True:  If file Passed validation.
            False: If file Failed validation.
            None:  If file was skipped, had no rules, or system error.
        """
        logger.info(f"Processing file: {filepath}")
        
        # 1. Hot-Reload Config
        self.config_manager.load_config() 
        self._configure_alerter()
        
        # 2. Route File (Find matching Ruleset)
        ruleset_name, metadata = self.router.route_file(filepath)
        logger.info(f"Routed to ruleset: {ruleset_name}")
        
        if not ruleset_name:
            logger.warning(f"No matching route found for {filepath}")
            return None # Processed but ignored

        # 3. Retrieve Rules
        rule_strings = self.config_manager.get_ruleset(ruleset_name)
        if not rule_strings:
            logger.error(f"Ruleset {ruleset_name} is empty or not found.")
            return None

        # 4. Parse Rules (using DSL)
        rules_text = "\n".join(rule_strings)
        parsed_rules = self.interpreter.parse_multiple_rules(rules_text)
        self.interpreter.rules = parsed_rules 
        
        # 5. Load Data
        rows = self.load_data(filepath)
        if not rows:
            logger.warning("No data found in file.")
            return None

        # 6. Execute Validation
        all_failures = []
        for i, row in enumerate(rows, 1):
            # Interpreter evaluates one row against all rules
            results = self.interpreter.validate_data(row)
            
            for res in results:
                if not res["passed"]:
                    # Capture detailed verification failure
                    fail = res.copy()
                    fail["row"] = i  # Add Row Number context
                    fail.update(metadata)
                    all_failures.append(fail)

        # 7. Action / Alerting
        if all_failures:
            logger.error(f"Validation failed with {len(all_failures)} errors.")
            self.alerter.trigger_alert(filepath, ruleset_name, all_failures)
            return False # FAILED
        else:
            logger.info("Validation successful.")
            return True # PASSED
