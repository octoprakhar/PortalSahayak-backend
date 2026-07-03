import time
from worker.facility_worker.FacilityWorker import FacilityWorker

from constants.Commands import Commands
from all_models.WorkerContext import WorkerContext
from all_models.UserRegistrationMetadata import UserRegistrationMetadata
from all_models.Message import Message

worker_context = WorkerContext(userName="",password="",address="",mobile_number="",planned_date="",user_registration_metadata=UserRegistrationMetadata(user_name="",district_id=45,health_block_id=220,state_id=23,mht_code=123297))

facilityWorker = FacilityWorker(job_id='abc',worker_context=worker_context)

facilityWorker.start()

facilityWorker.send(message=Message(job_id='abc',command=Commands.START_FACILITY_DISCOVERY,payload={}))

time.sleep(20)
