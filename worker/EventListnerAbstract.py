from abc import ABC,abstractmethod

from all_models.WorkerEvent import WorkerEvent

class EventListnerAbstract(ABC):

    @abstractmethod
    def handle(self,event: WorkerEvent) -> None:
        """
        Each event handler must handle this event in it's own way
        """
