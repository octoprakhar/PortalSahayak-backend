from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

from services.RuntimeManager import RunTimeManager

def append_log(job_dir: Path, message: str):
    timestamp = datetime.utcnow().isoformat()
    with open(job_dir / "logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def launch_browser_job(job_id:str):
    runtime_manager = RunTimeManager(job_id)
    runtime_manager.launch_browser_instance()

def open_institution_page(job_id: str):
    runtime_manager = RunTimeManager(job_id=job_id)
    runtime_manager.start_select_institution_stage()

def start_child_screening(job_id: str):
    runtime_manager = RunTimeManager(job_id=job_id)
    runtime_manager.start_child_screening()