import re
import os
from typing import Optional, Dict, Tuple
from .config_manager import ConfigManager

class Router:
    """
    Routes files to their appropriate rule sets based on naming conventions.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def route_file(self, filepath: str) -> Tuple[Optional[str], Dict]:
        """
        Determine which ruleset applies to the given file.
        Returns (ruleset_name, metadata)
        """
        filename = os.path.basename(filepath)
        routes = self.config_manager.get_routes()
        
        for route in routes:
            pattern = route["pattern"]
            # Convert simple glob-like patterns to regex if needed, 
            # or expect regex in config. For now, assuming regex.
            
            match = re.search(pattern, filename)
            if match:
                # Extract named groups from regex as metadata
                metadata = match.groupdict()
                return route["ruleset"], metadata
                
        return None, {}
