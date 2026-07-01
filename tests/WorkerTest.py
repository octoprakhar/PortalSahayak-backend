from worker.ScreeningWorker import Worker
from constants.Commands import Commands
from all_models.Message import Message

## LEt's start with creating the worker
worker = Worker("job-1")

print(f"Initial state of the worker is : {worker.state}")

## Now let's give the first command to create job
create_job_message = Message(job_id="job-1",command=Commands.CREATE_JOB,payload={})
worker.mail_box.push(create_job_message)
worker.process_next_message()
print(worker.events)

select_institution_message = Message(job_id="job-1",command=Commands.INSTITUTION_SELECTED,payload={"institution_id": "it-234"})
worker.mail_box.push(select_institution_message)
worker.process_next_message()
print(worker.events)


## Bad path
worker2 = Worker("job-2")
create_job_message = Message(job_id="job-2",command=Commands.INSTITUTION_SELECTED,payload={"institution_id": "it-234"})
worker2.mail_box.push(create_job_message)
worker2.process_next_message()
print(worker2.events) ## Gives error 