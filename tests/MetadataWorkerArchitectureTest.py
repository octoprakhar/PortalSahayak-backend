from worker.institution_data.InstitutionDataWorker import InstitutionDataWorker
from all_models.WorkerContext import WorkerContext
from all_models.Message import Message
from constants.Commands import Commands
from all_models.ApplicationServices import ApplicationServices

from factory.WorkerFactory import WorkerFactory

import time

## Individual worker test
# workerContext = WorkerContext(userName="LALBARRA-R1",password="Trapti@1234",address="Khamghat",mobile_number="9191919191", planned_date="2026-06-27T12:35:33.000Z")

# institutionWorker = InstitutionDataWorker(job_id="f4a861f9-a355-4a9e-9dc8-97c07a1fe7bc",worker_context=workerContext)
# institutionWorker.start()

# institutionWorker.send(message=Message(job_id="f4a861f9-a355-4a9e-9dc8-97c07a1fe7bc",command=Commands.GET_INSTITUTION,payload={}))

## Working ====================


## Active worker store test
factory = WorkerFactory()

time.sleep(30)
