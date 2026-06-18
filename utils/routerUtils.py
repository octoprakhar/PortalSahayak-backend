from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import logging
from zoneinfo import ZoneInfo

from services.JobManager import JobManager
from all_models.JobLogs import JobLog
from constants.job_status import JobStatus
from constants.log_type import LogType

from all_models.InstitutionData import InstitutionData


from services.RuntimeManager import RunTimeManager

def append_log(job_dir: Path, message: str):
    timestamp = datetime.utcnow().isoformat()
    with open(job_dir / "logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def launch_browser_job(job_id:str):
    runtime_manager = RunTimeManager(job_id)
    try:
        runtime_manager.launch_browser_instance()
        runtime_manager.login_user()
        resulted_institution = runtime_manager.start_select_institution_stage()
        return resulted_institution
    except Exception as e:
        JobManager.update_job_status(
            job_id=job_id,
            status=JobStatus.FAILED
        )

        JobManager.add_log(job_id=job_id,log=JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message="Error occured while starting and logging user",
                    type=LogType.ERROR
                ))
        logging.exception(f"Error occured while starting and logging user as \n{e}")
        

    


def open_institution_page(job_id: str):
    runtime_manager = RunTimeManager(job_id=job_id)
    runtime_manager.start_select_institution_stage()

def start_child_screening(job_id: str, institution_data: InstitutionData | None = None, is_ANM_present: bool = False ):
    runtime_manager = RunTimeManager(job_id=job_id)
    runtime_manager.start_child_screening(is_ANM_Present=is_ANM_present, institution_data=institution_data)