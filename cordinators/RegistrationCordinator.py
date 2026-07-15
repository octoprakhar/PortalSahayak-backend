from worker.EventListnerAbstract import EventListnerAbstract

from all_models.WorkerEvent import WorkerEvent
from constants.Events import Events
from worker_repository.ActiveWorkerStore import ActiveWorkerStore

from constants.Commands import Commands
from constants.WorkerType import WorkerType
from all_models.Message import Message

from all_models.UserRegistrationMetadata import UserRegistrationMetadata
from all_models.PortalCredentials import PortalCredentials


class RegistrationCordinator(EventListnerAbstract):
    """
    THis cordinator helps to do the work after registration of the new user has done. 
    It is use to collect some of the metadata
    """

    def handle(self, event:WorkerEvent):
        if event.event == Events.REGISTRATION_METADATA_FETCHED:
            registrationMetadata: UserRegistrationMetadata = event.payload["registrationMetadata"]
            portalCredentials: PortalCredentials = event.payload["portalCredentials"]
            ## Give the command 
            # print(f"In cordinator, Got portalCredential of type : {type(event.payload['portalCredentials'])}, and value{event.payload['portalCredentials']}")
            facility_worker = ActiveWorkerStore.get_worker(job_id=event.job_id,worker_type=WorkerType.FACILITY_WORKER)
            facility_worker.send(message=Message(job_id=event.job_id,command=Commands.START_FACILITY_DISCOVERY,payload={"registrationMetadata":registrationMetadata, "portalCredentials": portalCredentials}))
