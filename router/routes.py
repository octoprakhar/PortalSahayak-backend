from fastapi import APIRouter,BackgroundTasks, File, Form, UploadFile, HTTPException, WebSocket,Request
from typing import Optional
import logging
import asyncio

from utils.routerUtils import append_log, launch_browser_job, open_institution_page,start_child_screening
from services.JobManager import JobManager
from constants.job_status import JobStatus
import random
from all_models.InstitutionData import InstitutionData
from constants.institution_type import InstitutionType

from worker_repository.ActiveWorkerStore import ActiveWorkerStore
from all_models.Message import Message
from factory.WorkerFactory import WorkerFactory
from constants.Commands import Commands
from websocket.WebsocketManager import WebsocketManger



router = APIRouter()
ws_manager = WebsocketManger()


@router.get("/health")
async def get_users():
    return {"status": "ok"}

@router.post("/create-job")
async def create_job(
    request: Request,
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

    

    ## Launching worker

    services = request.app.state.services
    

    try:
        ## Create the job
        jobManager = JobManager(address=address,mobileNumber=mobileNumber,file=file,date=date, userName=userName, password=password)
        job_id = await jobManager.create_job()
        
        workerFactory = WorkerFactory(application_services=services)
        worker = workerFactory.create(job_id=job_id)

        worker.start()
        worker.send(Message(job_id=job_id, command=Commands.CREATE_JOB, payload={}))
        return {
            "job_id": job_id,
            "data" : [InstitutionData(institution_plan_id=167015,institution_name="MOHGOVN BORI-1",planned_date="2026-06-24T00:00:00.000Z",institution_type=InstitutionType.AWC)] ## Only for now It will be received to the user through websocket

        }
    except Exception as e:
        logging.exception("routes.py: Error creating worker")
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

    # await ws_manager.send(job_id=job_id,message="Hello starting with first message")

    # await asyncio.sleep(3)

    # await ws_manager.send(job_id=job_id,message="Hello starting with first message")

@router.get("/jobs/{job_id}/get-status")
def get_status(job_id: str):
    
    try:
        jobStatus = JobManager.get_current_status(job_id)
        return {"status": jobStatus.value}
    except Exception as e:
        return {"status": JobStatus.FAILED.value, "error": str(e)}
    
@router.get("/test-send/{job_id}")
async def send_job(job_id:str):
    # await ws_manager.send(job_id=job_id, message=f"Hello starting with first message: {random.random()}")
    return {"status":200}
    

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
def start_job_screeninhg(background_task: BackgroundTasks,job_id: Optional[str] = Form(None),institution_plan_id: Optional[str] = Form(None),institution_name: Optional[str] = Form(None),institution_type_val: Optional[str] = Form(None),planned_date: Optional[str] = Form(None),is_anm_present: bool = Form(False)):
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
    
    institution_data = InstitutionData(institution_plan_id=institution_plan_id, institution_name=institution_name, institution_type=InstitutionType(value=institution_type_val), planned_date=planned_date)


    try:
        worker = ActiveWorkerStore.get_worker(job_id=job_id)
        worker.send(Message(job_id=job_id, command=Commands.INSTITUTION_SELECTED, payload={"institution_data":institution_data}))
        return {"status":"ok"}
    except Exception as e:
        return {"error":str(e)}
