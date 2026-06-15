from fastapi import APIRouter,BackgroundTasks, File, Form, UploadFile, HTTPException
from pathlib import Path
import uuid
import json
from datetime import datetime
from typing import Optional

from utils.routerUtils import append_log, launch_browser_job, open_institution_page,start_child_screening
from services.JobManager import JobManager
from services.RuntimeManager import RunTimeManager
from constants.job_status import JobStatus
import random
from all_models.JobLogs import JobLog


router = APIRouter()


@router.get("/health")
async def get_users():
    return {"status": "ok"}

@router.post("/create-job")
async def create_job(
    background_tasks: BackgroundTasks,
    address: Optional[str] = Form(None),
    mobileNumber: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    userName: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    file: UploadFile | None = File(None)
):
    """
    Request as : 
    address: string
    mobileNumber: String
    file: File

    Response as :
    job_id : string | Null
    """
    # Validate data
    if not address or not address.strip():
        raise HTTPException(
            status_code=400,
            detail="Address is required"
        )

    if not mobileNumber or not mobileNumber.strip():
        raise HTTPException(
            status_code=400,
            detail="Mobile number is required"
        )
    
    if not userName or not userName.strip():
        raise HTTPException(
            status_code=400,
            detail="UserName is required"
        )

    if not password or not password.strip():
        raise HTTPException(
            status_code=400,
            detail="Password is required"
        )
    
    if not date or not date.strip():
        raise HTTPException(
            status_code=400,
            detail="Screening month is required"
        )

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File is required"
        )

    ## Create the job
    jobManager = JobManager(address=address,mobileNumber=mobileNumber,file=file,date=date, userName=userName, password=password)
    job_id = await jobManager.create_job()

    ## Launching browser
    background_tasks.add_task(
    launch_browser_job,
    job_id
    )

    return {
        "job_id": job_id

    }

@router.get("/jobs/{job_id}/get-status")
def get_status(job_id: str):
    
    try:
        jobStatus = JobManager.get_current_status(job_id)
        return {"status": jobStatus.value}
    except Exception as e:
        return {"status": JobStatus.FAILED.value, "error": e.message}
    

@router.get("/jobs/{job_id}/logs")
def get_logs(job_id: str, after: Optional[str] = None):
    try:
        logs = JobManager.get_logs(job_id, after)
        return {"logs": logs}
    except Exception as e:
        return {"logs": [], "error": str(e)}
    
@router.post("/institutions-list")
def get_institutions_list(background_task: BackgroundTasks,job_id: Optional[str] = Form(None)):
    """
    Request:
    job_id: str

    Response:
    status: ok
    error: Nullable str
    """
    ## Validate data
    if not job_id or not job_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Job ID is required"
        )

    try:
        background_task.add_task(open_institution_page,job_id)
        return {"status":"ok"}
    except Exception as e:
        return {"error":e.message}


@router.post("/start-screening")
def start_job_screeninhg(background_task: BackgroundTasks,job_id: Optional[str] = Form(None)):
    """
    Request:
    job_id: str

    Response:
    status: ok
    error: Nullable str
    """
    ## Validate data
    if not job_id or not job_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Job ID is required"
        )

    try:
        background_task.add_task(start_child_screening,job_id)
        return {"status":"ok"}
    except Exception as e:
        return {"error":e.message}
