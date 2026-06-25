import logging

from worker.EventListnerAbstract import EventListnerAbstract

from constants.Events import Events
from all_models.WorkerEvent import WorkerEvent

class ReportListner(EventListnerAbstract):
    """
    This will help in saving report to persistant place either in file system, or database
    """
    def handle(self, event: WorkerEvent):
        if event.event == Events.REPORT_CREATED:
            ## Get success and failure report creator
            logging.info(f"ReportListner: Got success path as : {event.payload.get('success_path')}")
            logging.info(f"ReportListner: Got failure path as : {event.payload.get('failure_path')}")
           