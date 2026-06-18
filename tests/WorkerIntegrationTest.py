from worker_repository.ActiveWorkerStore import ActiveWorkerStore
from worker.Worker import Worker
from all_models.Message import Message
from constants.Commands import Commands

from all_models.InstitutionData import InstitutionData
from constants.institution_type import InstitutionType

import time

worker_store = ActiveWorkerStore()

worker1 = worker_store.create_worker("16e2f9ff-c1f9-4d48-b6c1-9648efdb4729")
worker2 = worker_store.create_worker("436e4150-e735-4377-83e3-5f231a31041d")
msg_w_1 = Message(job_id='16e2f9ff-c1f9-4d48-b6c1-9648efdb4729',command=Commands.CREATE_JOB, payload={})
msg_w_2 = Message(job_id='436e4150-e735-4377-83e3-5f231a31041d',command=Commands.CREATE_JOB, payload={})

## Construct message
msg_w_22 = Message(job_id='436e4150-e735-4377-83e3-5f231a31041d',command=Commands.INSTITUTION_SELECTED, payload={"institution_data" : InstitutionData(institution_plan_id=152514,institution_name="TEKADI NAHARTOLA 4",planned_date="2026-06-05T00:00:00.000Z",institution_type=InstitutionType.AWC)})

worker1.send(msg_w_1)
worker2.send(msg_w_2)
worker2.send(msg_w_22)

worker1.start()
worker2.start()


time.sleep(30)