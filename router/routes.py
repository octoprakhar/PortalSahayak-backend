from fastapi import APIRouter,BackgroundTasks, File, Form, UploadFile, HTTPException
from pathlib import Path
import uuid
import json
from datetime import datetime
from typing import Optional

from utils.routerUtils import append_log, launch_browser_job
from services.JobManager import JobManager
from services.RuntimeManager import RunTimeManager

router = APIRouter()


@router.get("/health")
async def get_users():
    return {"status": "ok"}

@router.post("/create-job")
async def create_job(
    background_tasks: BackgroundTasks,
    address: Optional[str] = Form(None),
    mobileNumber: Optional[str] = Form(None),
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

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File is required"
        )

    ## Create the job
    jobManager = JobManager(address=address,mobileNumber=mobileNumber,file=file)
    job_id = await jobManager.create_job()

    ## Launching browser
    background_tasks.add_task(
    launch_browser_job,
    job_id
    )
    
    return {
        "job_id": job_id

    }
