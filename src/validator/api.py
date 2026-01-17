from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from .config_manager import ConfigManager
from .engine import ValidationEngine
from .logger import logger
import os

app = FastAPI(title="File Validation System API", version="1.0")

# Serve Static Files (Dashboard)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="static")

config_manager = ConfigManager()
validation_engine = ValidationEngine()

@app.get("/stats")
def get_stats():
    """Return system statistics (Mocked for demo)"""
    return {
        "files_processed": 5000,
        "success_rate": 98.5,
        "active_alerts": 3,
        "system_status": "OPERATIONAL"
    }

@app.get("/logs")
def get_logs():
    """Get last 50 lines of logs"""
    log_file = "validator.log"
    if not os.path.exists(log_file):
        return {"logs": []}
    
    with open(log_file, "r") as f:
        lines = f.readlines()
        return {"logs": lines[-50:]}

# --- Data Models ---
class Ruleset(BaseModel):
    name: str
    rules: List[str]

class Route(BaseModel):
    pattern: str
    ruleset: str
    priority: int = 10

class ValidationRequest(BaseModel):
    filepath: str

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "active", "version": "1.0"}

@app.get("/rulesets")
def get_rulesets():
    logger.info("API: Fetching all rulesets")
    return config_manager.config.get("rulesets", {})

@app.post("/rulesets/{name}")
def create_update_ruleset(name: str, rules: List[str]):
    logger.info(f"API: Updating ruleset {name}")
    config_manager.add_ruleset(name, rules)
    return {"message": f"Ruleset {name} updated successfully"}

@app.get("/rulesets/{name}")
def get_ruleset(name: str):
    logger.info(f"API: Fetching ruleset {name}")
    rules = config_manager.get_ruleset(name)
    if not rules:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return {"name": name, "rules": rules}

@app.get("/routes")
def get_routes():
    logger.info("API: Fetching all routes")
    return config_manager.get_routes()

@app.post("/routes")
def create_route(route: Route):
    logger.info(f"API: Adding route for {route.pattern}")
    config_manager.add_route(route.pattern, route.ruleset, route.priority)
    return {"message": "Route added successfully"}

@app.post("/validate")
def validate_file(request: ValidationRequest, background_tasks: BackgroundTasks):
    """
    Trigger validation for a file. 
    Runs in background to avoid blocking API.
    """
    logger.info(f"API: Triggering validation for {request.filepath}")
    
    # Simple check if file exists (in real world could be S3 path etc)
    import os
    if not os.path.exists(request.filepath):
        # We might still return 202 accepted if we expect file to appear, 
        # but for now let's be strict
        raise HTTPException(status_code=404, detail="File not found on server")

    background_tasks.add_task(validation_engine.process_file, request.filepath)
    return {"message": "Validation scheduled", "filepath": request.filepath}
