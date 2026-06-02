from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

def append_log(job_dir: Path, message: str):
    timestamp = datetime.utcnow().isoformat()
    with open(job_dir / "logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def run_screening_workflow(job_id: str, job_dir: Path):
    append_log(job_dir, f"Job {job_id}: launching browser")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com")
        page.goto("https://rbsk.mohfw.gov.in/RBSK/login")

        append_log(job_dir, "Browser opened and login page loaded")