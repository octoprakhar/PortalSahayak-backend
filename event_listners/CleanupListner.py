from worker.EventListnerAbstract import EventListnerAbstract

from constants.Events import Events
from all_models.WorkerEvent import WorkerEvent
from worker_repository.ActiveWorkerStore import ActiveWorkerStore
from constants.WorkerType import WorkerType

class CleanupListner(EventListnerAbstract):
    """
    This will help in cleaning of the data, when worker has stopped working
    """
    def handle(self, event: WorkerEvent):
        if event.event == Events.INSTITUTION_FETCHED:
            ## Remove the institution selection worker
            worker = ActiveWorkerStore.get_worker(job_id=event.job_id, worker_type=WorkerType.INSTITUTION_DATA_WORKER)
            worker.shutdown()
            ActiveWorkerStore.remove_worker(job_id=event.job_id,worker_type=WorkerType.INSTITUTION_DATA_WORKER)

        if event.event == Events.JOB_FAILED or event.event == Events.REPORT_CREATED or event.event == Events.USER_AUTHENTICATION_FAILED:
            ## Shutdown all the worker, and remove it from the directory
            workers = ActiveWorkerStore.get_all_workers(job_id=event.job_id)
            for worker in workers.values():
                worker.shutdown()

            ActiveWorkerStore.remove_all_workers(job_id=event.job_id)

        if event.event == Events.REGISTRATION_METADATA_FETCHED:
            ## Remove the metadata worker
            worker = ActiveWorkerStore.get_worker(job_id=event.job_id, worker_type=WorkerType.USER_METADATA_WORKER)
            worker.shutdown()
            ActiveWorkerStore.remove_worker(job_id=event.job_id,worker_type=WorkerType.USER_METADATA_WORKER)
