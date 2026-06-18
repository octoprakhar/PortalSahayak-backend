from worker.EventListnerAbstract import EventListnerAbstract

class PrintListner(EventListnerAbstract):

    """
    Just testing whether event listners are working properly or not
    """
    def handle(self, event):
        print(
            f"{event.job_id} : {event.event} : {event.payload}"
        )