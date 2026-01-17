"""
FASTAPI Backend Service
-----------------------
Exposes a RESTful API for:
1. Dashboard Data (Stats, Logs)
2. Ruleset Management (CRUD for rules)
3. On-demand validation triggers

Run with: uvicorn src.validator.api:app --reload
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from .config_manager import ConfigManager
from .engine import ValidationEngine
from .logger import logger
import os

# Initialize app with metadata
app = FastAPI(
    title="Real-Time File Validation System API",
    description="Backend for managing rules, routing, and monitoring file validation.",
    version="5.0"
)

# --- Static Asset Serving (Dashboard) ---
# Ensures the frontend is accessible at /dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="static")

# --- Core Dependencies ---
config_manager = ConfigManager()
validation_engine = ValidationEngine()


# --- Pydantic Models (Request Validation) ---
class Ruleset(BaseModel):
    name: str
    rules: List[str]

class Route(BaseModel):
    pattern: str
    ruleset: str
    priority: int = 10

class ValidationRequest(BaseModel):
    filepath: str


# --- API Endpoints ---

@app.get("/")
def read_root():
    """Health Check Endpoint"""
    return {"status": "active", "system": "Validator V5", "version": "5.0"}

@app.get("/stats")
def get_stats():
    """
    Returns system telemetry calculated from the file system.
    """
    processed_dir = "processed"
    rejected_dir = "rejected"
    
    # Ensure dirs exist to avoid errors
    if not os.path.exists(processed_dir): os.makedirs(processed_dir)
    if not os.path.exists(rejected_dir): os.makedirs(rejected_dir)
    
    # Count files (excluding directories)
    count_processed = len([name for name in os.listdir(processed_dir) if os.path.isfile(os.path.join(processed_dir, name))])
    count_rejected = len([name for name in os.listdir(rejected_dir) if os.path.isfile(os.path.join(rejected_dir, name))])
    
    total = count_processed + count_rejected
    if total > 0:
        rate = round((count_processed / total) * 100, 1)
    else:
        rate = 100.0
        
    return {
        "files_processed": total,
        "success_rate": rate,
        "active_alerts": count_rejected,
        "system_status": "OPERATIONAL",
        "chart_data": {
            "valid": count_processed,
            "invalid": count_rejected
        }
    }

@app.get("/logs")
def get_logs():
    """
    Stream the last 50 lines of the application log file.
    Used by the dashboard 'Live Logs' widget.
    """
    log_file = "validator.log"
    if not os.path.exists(log_file):
        return {"logs": ["Log file not found."]}
    
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
            # Return last 50 lines, reversed for newest-first
            return {"logs": lines[-50:]}
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {"logs": [f"Error reading logs: {str(e)}"]}

# --- Ruleset Management ---

@app.get("/rulesets")
def get_rulesets():
    """List all configured validation rulesets."""
    logger.info("API: Fetching all rulesets")
    return config_manager.config.get("rulesets", {})

@app.get("/rulesets/{name}")
def get_ruleset(name: str):
    """Get a specific ruleset by name."""
    rules = config_manager.get_ruleset(name)
    if not rules:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return {"name": name, "rules": rules}

@app.post("/rulesets/{name}")
def create_update_ruleset(name: str, rules: List[str]):
    """Create or Update a ruleset dynamically."""
    logger.info(f"API: Updating ruleset '{name}'")
    config_manager.add_ruleset(name, rules)
    return {"message": f"Ruleset '{name}' updated successfully"}

# --- Routing Management ---

@app.get("/routes")
def get_routes():
    """List all file routing patterns."""
    return config_manager.get_routes()

@app.post("/routes")
def create_route(route: Route):
    """Add a new file routing rule."""
    logger.info(f"API: Adding route pattern '{route.pattern}' -> '{route.ruleset}'")
    config_manager.add_route(route.pattern, route.ruleset, route.priority)
    return {"message": "Route added successfully"}

# --- Execution ---

@app.post("/validate")
def validate_file(request: ValidationRequest, background_tasks: BackgroundTasks):
    """
    Manual Trigger: Force validation of a specific file.
    Runs validation in a background thread to prevent API blocking.
    """
    logger.info(f"API: Manual validation requested for {request.filepath}")
    
    if not os.path.exists(request.filepath):
        raise HTTPException(status_code=404, detail="File not found on server")

    # Dispatch to engine
    background_tasks.add_task(validation_engine.process_file, request.filepath)
    return {"message": "Validation scheduled", "filepath": request.filepath}

@app.get("/files/{category}")
def list_files(category: str):
    """
    List files in 'processed' or 'rejected' directories.
    """
    if category not in ["processed", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    target_dir = os.path.join(os.getcwd(), category)
    if not os.path.exists(target_dir):
        return {"files": []}
        
    try:
        # Get files with timestamp
        files = []
        for f in os.listdir(target_dir):
            full_path = os.path.join(target_dir, f)
            if os.path.isfile(full_path):
                stats = os.stat(full_path)
                files.append({
                    "name": f,
                    "size": stats.st_size,
                    "modified": stats.st_mtime
                })
        
        # Sort by newest first
        files.sort(key=lambda x: x["modified"], reverse=True)
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return {"files": []}
