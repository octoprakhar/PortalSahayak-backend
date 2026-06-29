from abc import ABC,abstractmethod

from all_models.WorkerEvent import WorkerEvent

from bridge.WorkerEventBridge import WorkerEventBridge

class EventListnerAbstract(ABC):

    def __init__(self,event_bridge: WorkerEventBridge):
        super().__init__()
        self.event_bridge = event_bridge
        

    @abstractmethod
    def handle(self,event: WorkerEvent) -> None:
        """
        Each event handler must handle this event in it's own way
        """
