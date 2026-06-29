import logging
import asyncio
from dataclasses import asdict

from worker.EventListnerAbstract import EventListnerAbstract


from constants.Events import Events
from all_models.WorkerEvent import WorkerEvent
from bridge.WorkerEventBridge import WorkerEventBridge

from websocket.WebsocketManager import WebsocketManger

class WebsocketListner(EventListnerAbstract):
    def __init__(self, event_bridge:WorkerEventBridge, websocket_manager: WebsocketManger):
        super().__init__(event_bridge)
        self.websocket_manager = websocket_manager
    def handle(self, event:WorkerEvent):

        if event.event == Events.LOG_MESSAGE:

            payload = {
                "event": event.event.value,
                "payload": {
                    "message": event.payload['message'],
                    "logType": event.payload["logType"].value,
                },
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(job_id=event.job_id,payload=payload))

        if event.event == Events.WORKER_STARTED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(job_id=event.job_id,payload=payload))

        if event.event == Events.LOGIN_COMPLETED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(job_id=event.job_id,payload=payload))
        
        if event.event == Events.INSTITUTION_FETCHED:
            payload = {
                "event": event.event.value,
                "payload": [
                    {
                        **asdict(inst),
                        "institution_type": inst.institution_type.value
                    }
                    for inst in event.payload
                ]
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(job_id=event.job_id,payload=payload))

        if event.event == Events.INSTITUTION_SELECTED:

            payload = {
                "event": event.event.value,
                "payload": {}
            }

            logging.info(f"Institution selected emitted")
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(job_id=event.job_id,payload=payload))
        
        if event.event == Events.JOB_FAILED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(job_id=event.job_id,payload=payload))

        if event.event == Events.REPORT_CREATED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(job_id=event.job_id,payload=payload))


