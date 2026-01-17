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
    Orchestrates the validation process.
    """
    
    def __init__(self, config_path="config.json"):
        self.config_manager = ConfigManager(config_path)
        self.router = Router(self.config_manager)
        self.interpreter = DSLInterpreter()
        self.alerter = AlertManager()
        
    def _configure_alerter(self):
        """Configure channels based on loaded config."""
        sys_config = self.config_manager.get_system_config()
        self.alerter.configure(sys_config)

    def load_data(self, filepath: str) -> List[Dict[int, Any]]:
        """
        Load data from file.
        Currently supports CSV without headers (treating them as 1C, 2C, etc).
        Returns list of dicts {1: val, 2: val...}
        """
        data = []
        try:
            with open(filepath, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    # Convert row to dict with 1-based indices (1C -> 1)
                    # Try to convert to numbers where possible for convenience
                    item = {}
                    for i, val in enumerate(row, 1):
                        val = val.strip()
                        # Try int, then float, then keep string
                        try:
                            item[i] = int(val)
                        except ValueError:
                            try:
                                item[i] = float(val)
                            except ValueError:
                                item[i] = val
                    data.append(item)
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
        return data

    def process_file(self, filepath: str):
        logger.info(f"Processing file: {filepath}")
        self.config_manager.load_config() # Reload config to get latest updates
        self._configure_alerter()
        
        # 1. Route the file
        ruleset_name, metadata = self.router.route_file(filepath)
        logger.info(f"Routed to ruleset: {ruleset_name}")
        
        if not ruleset_name:
            logger.warning(f"No matching route found for {filepath}")
            return

        # 2. Get Rules
        rule_strings = self.config_manager.get_ruleset(ruleset_name)
        if not rule_strings:
            logger.error(f"Ruleset {ruleset_name} is empty or not found.")
            return

        # 3. Parse Rules
        rules_text = "\n".join(rule_strings)
        parsed_rules = self.interpreter.parse_multiple_rules(rules_text)
        self.interpreter.rules = parsed_rules # Set rules for interpreter
        
        # 4. Load Data
        rows = self.load_data(filepath)
        if not rows:
            logger.warning("No data found in file.")
            return

        # 5. Validate
        all_failures = []
        for i, row in enumerate(rows, 1):
            results = self.interpreter.validate_data(row)
            for res in results:
                if not res["passed"]:
                    # Enrich failure with row number and metadata
                    fail = res.copy()
                    fail["row"] = i
                    fail.update(metadata)
                    all_failures.append(fail)

        # 6. Alert
        if all_failures:
            logger.error(f"Validation failed with {len(all_failures)} errors.")
            self.alerter.trigger_alert(filepath, ruleset_name, all_failures)
            return False # FAILED
        else:
            logger.info("Validation successful.")
            return True # PASSED
