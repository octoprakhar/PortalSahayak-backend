from fastapi import APIRouter,BackgroundTasks, File, Form, UploadFile, HTTPException
from pathlib import Path
import uuid
import json
from datetime import datetime
from typing import Optional

from utils.routerUtils import append_log, run_screening_workflow

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

    # Step 1 : create a job_id using uuid 
    job_id = str(uuid.uuid4())
    ## Step 2: create the folder like this inside 'jobs'(existing folder) as jobs/job_id/ and save that file here. It will be a csv file
    job_dir = Path("jobs") / job_id
    job_dir.mkdir(exist_ok=True,parents=True)

    ## Saving the uploaded file
    uploaded_file_path = job_dir / "uploaded.csv"
    file_bytes = await file.read()
    with open(uploaded_file_path, "wb") as f:
        f.write(file_bytes)



    ## Step 3: Append job.json file with this job in that same dir
    job_metadata = {
        "job_id": job_id,
        "status": "waiting_login",
        "created_at": datetime.utcnow().isoformat(),
        "address": address,
        "mobile_number": mobileNumber,
        "uploaded_file": "uploaded.csv",
    }
    
    with open(job_dir / "job.json", "w", encoding="utf-8") as f:
        json.dump(job_metadata, f, indent=2)

    ## Step 4: Inside that same folder make a Logs.txt file for that job, and save logs there for this job. I don't know how to do it.
    append_log(job_dir, "Successfully created job metadata. Starting browser workflow.")
    

    ## Step 5: Start a browser instance in playwright, I mean give it to a background task, and return response to user.
    background_tasks.add_task(run_screening_workflow, job_id, job_dir)
    
    return {
        "job_id": job_id

    }
