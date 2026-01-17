"""
File Router
-----------
Determines which Validation Ruleset applies to a given file.
Uses Regex (Regular Expression) matching on filenames.

Example:
    File: "Financial-2024.txt"
    Route: r"Financial-.*\.txt" -> "financial_rules"
"""

import re
import os
from typing import Optional, Dict, Tuple
from .config_manager import ConfigManager

class Router:
    """
    Logic for mapping filenames -> rulesets.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def route_file(self, filepath: str) -> Tuple[Optional[str], Dict]:
        """
        Scans configured routes by priority to find a match for the file.
        
        Args:
            filepath (str): Absolute or relative path to the file.
            
        Returns:
            Tuple[str, Dict]: (Ruleset Name, Extracted Metadata)
                              Returns (None, {}) if no match found.
        """
        filename = os.path.basename(filepath)
        routes = self.config_manager.get_routes()
        
        # Iterate through routes (assumed sorted by priority in ConfigManager)
        for route in routes:
            pattern = route["pattern"]
            
            # Attempt Regex Match
            match = re.search(pattern, filename)
            if match:
                # Capture regex named groups (e.g. (?P<date>\d+)) as metadata
                metadata = match.groupdict()
                return route["ruleset"], metadata
                
        return None, {}
