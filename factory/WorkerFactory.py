import logging

from worker.Worker import Worker
from worker.MetadataProvider import MetadataProvider
from worker_metadata_providers.FileMetadataProvider import FileMetadataProvider
from worker_repository.ActiveWorkerStore import ActiveWorkerStore
from worker.EventListnerAbstract import EventListnerAbstract

from event_listners.PrintListner import PrintListner
from event_listners.CleanupListner import CleanupListner
from event_listners.PersistenceListener import PersistenceListener

from all_models.WorkerContext import WorkerContext


class WorkerFactory:
    """
    This class will help in creating the worker, attaching it's listners, 
    registering the worker, etc. It means all the work which is needed at the 
    time of making a worker will be done here. So that we can just remove infrastructural 
    details in wherever we wanna use the worker.
    """

    def _get_context(self, job_id: str) -> WorkerContext:
        """
        Get metadata for the worker by calling the MetadataProvider class's family
        """
        metadataProvider: MetadataProvider = FileMetadataProvider()
        return metadataProvider.get_context(job_id=job_id)
    
    def _get_default_listeners(self) -> list[EventListnerAbstract]:
        return [ PrintListner(),PersistenceListener(), CleanupListner()]

    def _add_listners(self, worker: Worker):
        listeners = self._get_default_listeners()
        for listener in listeners:
            worker.events.subscribe(listner=listener)

    def create(self,job_id: str) -> Worker:
        """
        This method is responsible for creating the worker
        """

        try:
            ## Step 1 Get worker context/metadata
            worker_cotext: WorkerContext = self._get_context(job_id=job_id)

            ## Step 2: Create the worker
            worker = ActiveWorkerStore.create_worker(job_id=job_id, worker_context=worker_cotext)

            ## Step 3: Add listeners to it 
            self._add_listners(worker=worker)

            return worker
        except Exception as e:
            logging.exception("WorkerFactory: Error occured while making the worker")
            raise
