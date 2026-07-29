from fastapi import APIRouter, File, Form, UploadFile, HTTPException, WebSocket,Request
from typing import Optional
import logging
from postgrest.exceptions import APIError


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
from all_models.dto.request.FacilityMappingRequest import FacilityMappingRequest
from all_models.FacilityCatalog import FacilityCatalog
from all_models.ClassRange import ClassRange
from repository.UserRepository import UserRepository
from repository.JobRepository import JobRepository
from database.model.User import User
from database.model.Job import Job
from database.model.MetadataForJobCreation import MetadataForJobCreation



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
        ## Save user in db
        user_repository: UserRepository = services.user_repository

        user = User(user_name=userName, password=password)
        user_id = user_repository.create(user=user)

        ## Create the metadata collector worker
        ## Since this is a secondary type job, for user creation, so we will give userId as a job_id. Because here we are not creating anything
        workerFactory = WorkerFactory(application_services=services)
        registration_metadata_worker = workerFactory.create(user_id=user_id, worker_type=WorkerType.USER_METADATA_WORKER)
        registration_metadata_worker.send(message=Message(job_id=user_id,command=Commands.GET_USER_METADATA,payload={}))
        ## Just create the worker, not send the event
        facility_worker = workerFactory.create(user_id=user_id, worker_type=WorkerType.FACILITY_WORKER)

        return {"user_id": user_id}

    except APIError as e:
        logging.exception(e)

        # PostgreSQL unique violation
        if e.code == "23505":
            raise HTTPException(
                status_code=409,
                detail="User already exists."
            )

        raise HTTPException(
            status_code=500,
            detail="Database error."
        )
    
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")


@router.post("signin-user")
async def signin_user():
    #step 1: check for database
    # if ready, then send send success

    #step 2: Start with validating username and password, and send the userID
    pass
    
@router.post("/map-facility")
async def map_facility(data: FacilityMappingRequest,request:Request):
    services = request.app.state.services
    user_repository: UserRepository = services.user_repository
    selected_facility = data.selected_facility
    user_id = data.user_id
    logging.info(f"Called map facility with got selected_facility as {selected_facility}")

    if not user_id or not user_id.strip():
        raise HTTPException(
            status_code=400,
            detail="User ID is required"
        )
    
    if not selected_facility:
        raise HTTPException(
            status_code=400,
            detail="Selected Facility is required"
        )
    try:

        user = user_repository.get_by_userId(user_id=user_id)

        if not user:
            raise HTTPException(
                                status_code=400,
                                detail="Wrong userid"
                            )

        catalog = user.full_facility_catalog

        if not catalog:
            raise HTTPException(status_code=500,detail="Internal error occured.")
        

        mandatory_types = [
            "District Level Facility",
            "Block Level Facility",
            "NRC",
        ]

        # DEIC mandatory only if catalog has DEIC
        if catalog.get("DEIC"):
            mandatory_types.append("DEIC")
        
        ## Check all 3-4 types, block level, district level, nrc, and deic(if present), is there in dict or not, if not return error
        ## Check mandatory facility type
        for facility_type in mandatory_types:
            if facility_type not in selected_facility:
                raise HTTPException(
                    status_code=400,
                    detail=f"{facility_type} is required."
                )
            
        ## Validating every facility mapping

        for facility_type, facility_name in selected_facility.items():

            # Unknown facility type
            if facility_type not in catalog:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown facility type '{facility_type}'."
                )

            catalog_facilities = catalog[facility_type]

            # Catalog has no facilities for this type
            if len(catalog_facilities) == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"{facility_type} has no available facilities."
                )

            # Must be exactly one string
            if not isinstance(facility_name, str):
                raise HTTPException(
                    status_code=400,
                    detail=f"{facility_type} must have exactly one selected facility."
                )

            facility_name = facility_name.strip()

            if not facility_name:
                raise HTTPException(
                    status_code=400,
                    detail=f"{facility_type} cannot be empty."
                )

            # Must exist under same facility type
            if facility_name not in catalog_facilities:
                raise HTTPException(
                    status_code=400,
                    detail=f"'{facility_name}' is not a valid {facility_type}."
                )

        ##TODO: When db will be there Check facility names must match with the one of the facility names of the catalog. catalog must be saved inside catalog table to avoid sql injection

        ## Save that mapped facility in user.json UserMetadata, mapped_Facility
        # jobManager.saved_mapped_facility(job_id=job_id, mapped_facility=selected_facility)
        user_repository.update_selected_facility(user_id=user_id, select_facility=selected_facility)
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")

    ## Return jobId.
    return {"user_id":user_id}



    
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    This endpoint catches the React client when it sends a connection request
    using a specific job_id.
    """
    # Hand off the live websocket and its related job_id to our manager
    ws_manager = websocket.app.state.services.websocket_manager
    await ws_manager.connect(websocket, user_id)
    

@router.post("/post-job-metadata")
async def post_job_metadata(
    request: Request,
    is_anm_present: Optional[bool] = Form(None),
    from_class: Optional[int] = Form(None),
    to_class: Optional[int] = Form(None),
    address: Optional[str] = Form(None),
    mobileNumber: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    existing_limit: Optional[int] = Form(None)
    

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
    
    if not user_id or not user_id.strip():
        raise HTTPException(
            status_code=400,
            detail="User ID is required"
        )
    class_range = None

    if from_class and to_class:
        class_range = ClassRange(from_class=from_class, to_class=to_class) 
    
    try:
        # jobManager = JobManager() ## For testing
        # jobManager.store_job_metadata(job_id=job_id, address=address,mobile_number=mobileNumber,screening_date=date,is_anm_present=is_anm_present, class_range=class_range, existing_limit = existing_limit)

        #create the job
        job_repo: JobRepository = services.job_repository

        job_id = job_repo.create(job_creation_metadata=MetadataForJobCreation(user_id=user_id,status=JobStatus.IDLE, address=address, mobile_number=mobileNumber, planned_date=date, class_range= class_range, is_anm_present=is_anm_present, existing_limit=existing_limit))

        ## Now create worker for institution work
        workerFactory = WorkerFactory(application_services=services)
        institution_worker = workerFactory.create(user_id=user_id,job_id=job_id, worker_type=WorkerType.INSTITUTION_DATA_WORKER)
        institution_worker.send(message=Message(job_id=job_id,command=Commands.GET_INSTITUTION,payload={"planned_date":date}))
        return {"job_id": job_id}
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")

@router.post("/select-institution")
def select_institution(request: Request,user_id:Optional[str] = Form(None), job_id: Optional[str] = Form(None),institution_plan_id: Optional[str] = Form(None),institution_name: Optional[str] = Form(None),institution_type_val: Optional[str] = Form(None),planned_date: Optional[str] = Form(None),is_anm_present: bool = Form(False)):
    """
    Save these data in job metadata, for the job, and update the jobstatus
    """
    ## Validate data
    if not job_id or not job_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Job ID is required"
        )

    if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=400,
                detail="User ID is required"
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
        # jobManager = JobManager()
        # jobManager.upload_institution_data(job_id=job_id,institution_data=institution_data)
        ## Upload the institution
        services = request.app.state.services
        job_repo: JobRepository = services.job_repository

        job_id = job_repo.upload_institution_data(job_id=job_id, institution_data=institution_data)

        return {"job_id":job_id}
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")



@router.post("/start-screening")
def start_job_screeninhg(request:Request,user_id: Optional[str] = Form(None),job_id: Optional[str] = Form(None),uploaded_file: UploadFile = File(...)):
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

    if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=400,
                detail="User ID is required"
            )
    ## Let's assume file is present
    ## No validation for now

    services = request.app.state.services
    job_repo: JobRepository = services.job_repository
    user_repo : UserRepository = services.user_repository
    


    try:

        logging.info("Request came in Upload children")
        
        ## Save the file in persistant place
        # jobManager = JobManager()
        # jobManager.upload_file(job_id=job_id,uploaded_file=uploaded_file)

        # user_metadata = jobManager.get_user_metadata(job_id=job_id)

        # ## Get uploaded file path
        # job_metadata = JobManager.get_job_metadata(job_id=job_id)
        file_path = job_repo.upload_file(job_id=job_id,file=uploaded_file)
        file_url = job_repo.get_uploaded_file_url(job_id=job_id, file_path=file_path)

        user_metadata = user_repo.get_by_userId(user_id=user_id)
        job_metadata = job_repo.get_job_by_job_id(job_id=job_id)



        if not job_metadata:
            logging.error(f"Can't get job metadata")
            return {"error": "Cannot find user metadata."}
        
        # logging.info(f"Got file url : {file_url}")
        
        
        ## Create screening worker and pass the command for start screening
        workerFactory = WorkerFactory(application_services=services)
        screening_worker = workerFactory.create(user_id=user_id,job_id=job_id, worker_type=WorkerType.SCREENING_WORKER)
        screening_worker.send(message=Message(job_id=job_id,command=Commands.START_SCREENING, payload={"institution_name":job_metadata.institution_data.institution_name, "institution_plan_id":job_metadata.institution_data.institution_plan_id, "institution_type": job_metadata.institution_data.institution_type, "planned_date": job_metadata.planned_date, "uploaded_file_url": file_url, "address": job_metadata.address, "mobile_number": job_metadata.mobile_number,"selected_facility":user_metadata.selected_facility,"is_ANM_Present":job_metadata.is_anm_present, "class_range": job_metadata.class_range if job_metadata.institution_data.institution_type == InstitutionType.SCHOOL else None, "existing_limit": job_metadata.existing_limit}))
        return {"status":"ok","job_id":job_id}
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500,detail="Internal error occured.")
