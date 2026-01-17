"""
Configuration Manager
---------------------
Handles loading, saving, and querying of system configuration.
Persists state in 'config.json'.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class ConfigManager:
    """
    Interface for 'config.json'.
    Methods are thread-safe enough for our usage (single writer via API, mostly readers).
    """
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "routes": [],
            "rulesets": {},
            "system_config": {}
        }
        self.load_config()

    def load_config(self):
        """Reload configuration from disk."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"[Config] Error loading file: {e}")

    def save_config(self):
        """Persist current configuration to disk."""
        self.config["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"[Config] Error saving file: {e}")

    # --- Ruleset Operations ---
    def add_ruleset(self, name: str, rules: List[str]):
        """Define a new validation ruleset."""
        self.config["rulesets"][name] = rules
        self.save_config()

    def get_ruleset(self, name: str) -> List[str]:
        return self.config["rulesets"].get(name, [])

    # --- Routing Operations ---
    def add_route(self, pattern: str, ruleset_name: str, priority: int = 10):
        """
        Map a filename pattern to a ruleset.
        Overwrites existing routes with the same pattern.
        """
        # Filter out existing with same pattern
        self.config["routes"] = [r for r in self.config["routes"] if r["pattern"] != pattern]
        
        self.config["routes"].append({
            "pattern": pattern,
            "ruleset": ruleset_name,
            "priority": priority
        })
        # Keep sorted by priority
        self.config["routes"].sort(key=lambda x: x["priority"], reverse=True)
        self.save_config()

    def get_routes(self) -> List[Dict]:
        return self.config["routes"]

    # --- System Config Operations ---
    def set_system_config(self, config: Dict):
        self.config["system_config"] = config
        self.save_config()

    def get_system_config(self) -> Dict:
        return self.config.get("system_config", {})
