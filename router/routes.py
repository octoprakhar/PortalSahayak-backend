from fastapi import APIRouter,BackgroundTasks, File, Form, UploadFile, HTTPException, WebSocket,Request
from typing import Optional
import logging
from io import BytesIO

from services.JobManager import JobManager
from constants.job_status import JobStatus
import random
from all_models.InstitutionData import InstitutionData
from constants.institution_type import InstitutionType

from worker_repository.ActiveWorkerStore import ActiveWorkerStore
from all_models.Message import Message
from factory.WorkerFactory import WorkerFactory
from constants.Commands import Commands
from constants.WorkerType import WorkerType
from websocket.WebsocketManager import WebsocketManger



router = APIRouter()
ws_manager = WebsocketManger()


@router.get("/health")
async def get_users():
    return {"status": "ok"}

@router.post("/register-signin-user")
async def register_job(
    request: Request,
    userName: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    services = request.app.state.services
    logging.info("Request came in register sign in user.")
    
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
    
    try:
        jobManager = JobManager() ## For testing
        job_id = jobManager.construct_job()
        jobManager.store_user_data(job_id=job_id, username=userName,password=password)

        ## Create the metadata collector worker
        workerFactory = WorkerFactory(application_services=services)
        registration_metadata_worker = workerFactory.create(job_id=job_id, worker_type=WorkerType.USER_METADATA_WORKER)
        registration_metadata_worker.send(message=Message(job_id=job_id,command=Commands.GET_USER_METADATA,payload={}))

        return {"job_id": job_id}
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")
    
@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    This endpoint catches the React client when it sends a connection request
    using a specific job_id.
    """
    # Hand off the live websocket and its related job_id to our manager
    ws_manager = websocket.app.state.services.websocket_manager
    await ws_manager.connect(websocket, job_id)
    

@router.post("/post-job-metadata")
async def post_job_metadata(
    request: Request,
    address: Optional[str] = Form(None),
    mobileNumber: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    job_id: Optional[str] = Form(None)
):
    
    """
    Save job metadata in the file, and start with doing next thing. Create Metadata Worker, and get the institution list for that date.
    And then start running 
    """
    logging.info("Request came in Post job metadata.")
    services = request.app.state.services
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
    
    if not date or not date.strip():
        raise HTTPException(
            status_code=400,
            detail="Screening month is required"
        )
    
    if not job_id or not job_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Job ID is required"
        )
    
    try:
        jobManager = JobManager() ## For testing
        jobManager.store_job_metadata(job_id=job_id, address=address,mobile_number=mobileNumber,screening_date=date)

        ## Now create worker for institution work
        workerFactory = WorkerFactory(application_services=services)
        institution_worker = workerFactory.create(job_id=job_id, worker_type=WorkerType.INSTITUTION_DATA_WORKER)
        institution_worker.send(message=Message(job_id=job_id,command=Commands.GET_INSTITUTION,payload={}))
        return {"job_id": job_id}
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")

@router.post("/select-institution")
def select_institution(job_id: Optional[str] = Form(None),institution_plan_id: Optional[str] = Form(None),institution_name: Optional[str] = Form(None),institution_type_val: Optional[str] = Form(None),planned_date: Optional[str] = Form(None),is_anm_present: bool = Form(False)):
    """
    Save these data in job metadata, for the job, and update the jobstatus
    """
    ## Validate data
    if not job_id or not job_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Job ID is required"
        )
    
    if not institution_plan_id or not institution_plan_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Institution ID is required"
        )
    
    if not institution_name or not institution_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Institution name is required"
        )
    
    if not institution_type_val or not institution_type_val.strip():
        raise HTTPException(
            status_code=400,
            detail="Institution type is required"
        )
    
    if not planned_date or not planned_date.strip():
        raise HTTPException(
            status_code=400,
            detail="Planned date is required"
        )
    
    logging.info("Request came in Select institution.")
    
    institution_data = InstitutionData(institution_plan_id=institution_plan_id, institution_name=institution_name, institution_type=InstitutionType(value=institution_type_val), planned_date=planned_date)

    try:
        jobManager = JobManager()
        jobManager.upload_institution_data(job_id=job_id,institution_data=institution_data)
        return {"job_id":job_id}
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")



@router.post("/start-screening")
def start_job_screeninhg(request:Request,job_id: Optional[str] = Form(None),uploaded_file: UploadFile = File(...)):
    """
    It will take all children data, and then run the Screening Worker.
    Request:
    job_id: str

    Response:
    status: ok
    error: Nullable str
    """

    services = request.app.state.services

    if not job_id or not job_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Job ID is required"
        )
    ## Let's assume file is present
    ## No validation for now
    


    try:

        logging.info("Request came in Upload children")
        
        ## Save the file in persistant place
        jobManager = JobManager()
        jobManager.upload_file(job_id=job_id,uploaded_file=uploaded_file)

        ## Create screening worker and pass the command for start screening
        workerFactory = WorkerFactory(application_services=services)
        screening_worker = workerFactory.create(job_id=job_id, worker_type=WorkerType.SCREENING_WORKER)
        screening_worker.send(message=Message(job_id=job_id,command=Commands.START_SCREENING, payload={}))
        return {"status":"ok","job_id":job_id}
    except Exception as e:
        return {"error":str(e)}
