from worker_repository.ActiveWorkerStore import ActiveWorkerStore
from worker.ScreeningWorker import Worker
from event_listners.PrintListner import PrintListner
from all_models.Message import Message
from constants.Commands import Commands

from all_models.InstitutionData import InstitutionData
from constants.institution_type import InstitutionType

import time

worker_store = ActiveWorkerStore()
printListner = PrintListner()

worker2 = worker_store.create_worker("26b41f71-a5c6-4309-8b6e-2ddd5c955469")
worker2.events.subscribe(printListner)
msg_w_2 = Message(job_id='26b41f71-a5c6-4309-8b6e-2ddd5c955469',command=Commands.CREATE_JOB, payload={})

## Construct message
msg_w_22 = Message(job_id='26b41f71-a5c6-4309-8b6e-2ddd5c955469',command=Commands.INSTITUTION_SELECTED, payload={"institution_data" : InstitutionData(institution_plan_id=152514,institution_name="TEKADI NAHARTOLA 4",planned_date="2026-06-05T00:00:00.000Z",institution_type=InstitutionType.AWC)})

worker2.send(msg_w_2)
worker2.send(msg_w_22)

worker2.start()


time.sleep(30)