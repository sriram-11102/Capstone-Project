import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class ConfigManager:
    """
    Manages configuration for file validation rules and routing.
    Stores configs in a simple JSON format.
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
        """Load configuration from disk if it exists."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Save current configuration to disk."""
        self.config["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_ruleset(self, name: str, rules: List[str]):
        """Add or update a named set of DSL rules."""
        self.config["rulesets"][name] = rules
        self.save_config()

    def get_ruleset(self, name: str) -> List[str]:
        """Retrieve a ruleset by name."""
        return self.config["rulesets"].get(name, [])

    def add_route(self, pattern: str, ruleset_name: str, priority: int = 10):
        """
        Add a file routing rule.
        pattern: Regex or Glob pattern (we'll implement basic regex in router)
        ruleset_name: Name of ruleset to apply
        priority: Higher number = Higher priority
        """
        # Remove existing route if pattern exists
        self.config["routes"] = [r for r in self.config["routes"] if r["pattern"] != pattern]
        
        self.config["routes"].append({
            "pattern": pattern,
            "ruleset": ruleset_name,
            "priority": priority
        })
        # Sort routes by priority (descending)
        self.config["routes"].sort(key=lambda x: x["priority"], reverse=True)
        self.save_config()

    def get_routes(self) -> List[Dict]:
        """Return all configured routes."""
        return self.config["routes"]

    def set_system_config(self, config: Dict):
        """Set system-wide configuration (alerts, etc)."""
        self.config["system_config"] = config
        self.save_config()

    def get_system_config(self) -> Dict:
        """Get system-wide configuration."""
        return self.config.get("system_config", {})
