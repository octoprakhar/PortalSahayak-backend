from worker.EventListnerAbstract import EventListnerAbstract

from constants.Events import Events
from all_models.WorkerEvent import WorkerEvent
from worker_repository.ActiveWorkerStore import ActiveWorkerStore

class CleanupListner(EventListnerAbstract):
    """
    This will help in cleaning of the data, when worker has stopped working
    """
    def handle(self, event: WorkerEvent):
        if event.event == Events.JOB_FAILED or event.event == Events.REPORT_CREATED:
            ## Shutdown the worker, and remove it from the directory
            worker = ActiveWorkerStore.get_worker(job_id=event.job_id)
            worker.shutdown()
            ActiveWorkerStore.remove_worker(job_id=event.job_id)
