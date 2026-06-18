from all_models.WorkerEvent import WorkerEvent
from worker.EventListnerAbstract import EventListnerAbstract


class EventBus:
    """
    Each worker will have it's own Event bus , where whenever worker
    emits an event, it will be put in the queue of the events of that worker
    """

    def __init__(self):
        self.event_listners: list[EventListnerAbstract] = []

    def subscribe(self,listner: EventListnerAbstract):
        """
        When any event Listner calls this method. I will put it in my event_listners list
        """
        if listner in self.event_listners:
            return
        
        self.event_listners.append(listner)

    def unsubscribe(self,listner: EventListnerAbstract):
        """
        Remove that listner from listening list
        """
        if listner in self.event_listners:
            self.event_listners.remove(listner)
    
    def publish(self,event:WorkerEvent):
        """
        New event has arrived call all the event listners handle() method
        """
        for listner in self.event_listners:
            listner.handle(event)


