from worker.EventListnerAbstract import EventListnerAbstract

from all_models.WorkerEvent import WorkerEvent
from constants.Events import Events
from constants.job_status import JobStatus
from repository.UserRepository import UserRepository
from repository.JobRepository import JobRepository

class PersistenceListener(EventListnerAbstract):

    """
    This event listner does all the works, from creating the report, adding logs, updating status etc. 
    I mean all types of work related to database/file management. It will handle all types of persistant work.
    """
    def __init__(self, event_bridge, userRepository: UserRepository, jobRepository: JobRepository, user_id: str, job_id: str | None):
        super().__init__(event_bridge)
        self.user_repository = userRepository
        self.job_repository = jobRepository
        self.user_id = user_id
        self.job_id = job_id

    def _update_job_status(self, newStatus: JobStatus, job_id: str):
        self.job_repository.update_job_status(job_id=job_id, new_status=newStatus)


    def handle(self, event:WorkerEvent):

        if event.event == Events.LOG_MESSAGE:
            payload = event.payload
            job_id = event.job_id
            message = payload["message"]
            logType = payload["logType"]


            # self._add_log(message=message,type=logType,job_id=job_id)
            pass

        if event.event == Events.WORKER_STARTED:
            self._update_job_status(newStatus=JobStatus.LOGGING_IN,job_id=event.job_id)
            # self._add_log(message="Work started, waiting for login in",type=LogType.SUCCESS, job_id=event.job_id)

        if event.event == Events.LOGIN_COMPLETED:
            self._update_job_status(newStatus=JobStatus.WAITING_INSTITUTION, job_id=event.job_id)
            # self._add_log(message="Logged in succesfully, Waiting for institution to get selected", type=LogType.SUCCESS, job_id=event.job_id)

        if event.event == Events.REGISTRATION_METADATA_FETCHED:
            # self._add_log(message="User registration metadata fetched.",type=LogType.SUCCESS,job_id=event.job_id)
            ## Save registration metadata using jobmanager
            self.user_repository.update_registration_metadata(user_id=self.user_id,registrationMetadata=event.payload["registrationMetadata"])


        if event.event == Events.JOB_FAILED:
            self._update_job_status(newStatus=JobStatus.FAILED, job_id=event.job_id)
            ## TODO: In the future, if the job failed in between saving some children data, so just from the uploaded file reduce that data that 
            ## had already been entered and then maybe make a new row in db with new job, with remaining children and Idle Jobstatus, to try rerun
            ## It ones more

            ## If it has failed in screening time just compile and save it both successful child and failed child report in db.

        if event.event == Events.INSTITUTION_FETCHED:
            pass

        if event.event == Events.FACILITY_CATALOG_FETCHED:
            ## TODO: save this fetched facility with user id, to the db
            ## For now saving it inside jobs/job_id/catalog.json
            self.user_repository.update_full_facility_catalog(user_id=self.user_id,full_facility_catalog=event.payload["facility_catalog"])


        if event.event == Events.INSTITUTION_SELECTED:
            ## TODO : save that institution in the persistant database.
            self._update_job_status(newStatus=JobStatus.RUNNING, job_id=event.job_id)
            

        if event.event == Events.REPORT_CREATED:
            ### TODO: The runtime manager, will give some files, like success_child list, with all the children which has correctly been screened
            ## With their disease(if randomly selected), or other things, whether it was earlier SAM and we had converted, etc. It will also send 
            ## Screening failed child, and validation failed child, we need to compile and save the report here.
            self._update_job_status(newStatus=JobStatus.COMPLETED, job_id=event.job_id)
        
        if event.event == Events.USER_AUTHENTICATION_FAILED:
            ### Remove the whole job related persistant data
            pass