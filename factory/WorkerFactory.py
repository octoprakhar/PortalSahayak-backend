import logging

from worker.WorkerAbstract import WorkerAbstract
from worker.ScreeningWorker import ScreeningWorker
from worker.institution_data.InstitutionDataWorker import InstitutionDataWorker
from worker.user_metadata.UserMetadataWorker import UserMetadataWorker
from worker.facility_worker.FacilityWorker import FacilityWorker

from worker.MetadataProvider import MetadataProvider
from worker_metadata_providers.DatabaseMetadataProvider import DatabaseMetadataProvider
from worker_repository.ActiveWorkerStore import ActiveWorkerStore
from worker.EventListnerAbstract import EventListnerAbstract

from event_listners.PrintListner import PrintListner
from event_listners.CleanupListner import CleanupListner
from event_listners.PersistenceListener import PersistenceListener
from event_listners.ReportListner import ReportListner
from event_listners.WebsocketListner import WebsocketListner

from cordinators.RegistrationCordinator import RegistrationCordinator

from all_models.WorkerContext import WorkerContext
from all_models.ApplicationServices import ApplicationServices

from constants.WorkerType import WorkerType

class WorkerFactory:
    """
    This class will help in creating the worker, attaching it's listners, 
    registering the worker, etc. It means all the work which is needed at the 
    time of making a worker will be done here. So that we can just remove infrastructural 
    details in wherever we wanna use the worker.
    """
    def __init__(self,application_services: ApplicationServices):
        self.services = application_services
        self.WORKER_MAP: dict[WorkerType, type[WorkerAbstract]] = {
            WorkerType.INSTITUTION_DATA_WORKER: InstitutionDataWorker,
            WorkerType.SCREENING_WORKER: ScreeningWorker,
            WorkerType.USER_METADATA_WORKER: UserMetadataWorker,
            WorkerType.FACILITY_WORKER: FacilityWorker
        }

    def _get_context(self, user_id: str) -> WorkerContext:
        """
        Get metadata for the worker by calling the MetadataProvider class's family
        """
        # metadataProvider: MetadataProvider = FileMetadataProvider()
        # return metadataProvider.get_context(job_id=job_id)
        metadataProvider : MetadataProvider = DatabaseMetadataProvider()
        return metadataProvider.get_context(user_id=user_id, userReposity=self.services.user_repository)
    
    def _get_default_listeners(self, user_id: str, job_id : str | None) -> list[EventListnerAbstract]:
        return [ PrintListner(event_bridge=self.services.event_bridge),PersistenceListener(event_bridge=self.services.event_bridge, userRepository=self.services.user_repository,jobRepository=self.services.job_repository, user_id=user_id, job_id=job_id), CleanupListner(event_bridge=self.services.event_bridge), ReportListner(event_bridge=self.services.event_bridge), WebsocketListner(event_bridge=self.services.event_bridge,websocket_manager=self.services.websocket_manager, user_id=user_id), RegistrationCordinator(event_bridge=self.services.event_bridge)]

    def _add_listners(self, worker: WorkerAbstract, user_id: str, job_id: str | None):
        listeners = self._get_default_listeners(user_id=user_id, job_id=job_id)
        for listener in listeners:
            worker.events.subscribe(listner=listener)

    def create(self, worker_type: WorkerType, user_id: str, job_id: str = None) -> WorkerAbstract:
        """
        This method is responsible for creating the worker
        """

        try:
            ## Step 1 Get worker context/metadata
            worker_context = self._get_context(user_id=user_id)

            worker_cls = self.WORKER_MAP[worker_type]

            worker = worker_cls(
                job_id=job_id if job_id else user_id,
                worker_context=worker_context,
            )

            self._add_listners(worker=worker, user_id=user_id, job_id=job_id)
            worker.start()

            ActiveWorkerStore.register_worker(
                job_id=job_id if job_id else user_id,
                worker_type=worker_type,
                worker=worker,
            )

            return worker

        except Exception as e:
            logging.exception("WorkerFactory: Error occured while making the worker")
            raise
