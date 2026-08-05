import logging
import asyncio
from dataclasses import asdict

from worker.EventListnerAbstract import EventListnerAbstract


from constants.Events import Events
from all_models.WorkerEvent import WorkerEvent
from all_models.FacilityCatalog import FacilityCatalog
from bridge.WorkerEventBridge import WorkerEventBridge


from websocket.WebsocketManager import WebsocketManger

class WebsocketListner(EventListnerAbstract):
    def __init__(self, event_bridge:WorkerEventBridge, websocket_manager: WebsocketManger, user_id: str):
        super().__init__(event_bridge)
        self.websocket_manager = websocket_manager
        self.user_id = user_id
    def handle(self, event:WorkerEvent):

        if event.event == Events.LOG_MESSAGE:

            # payload = {
            #     "event": event.event.value,
            #     "payload": {
            #         "message": event.payload['message'],
            #         "logType": event.payload["logType"].value,
            #     },
            # }
            # self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))
            pass

        if event.event == Events.WORKER_STARTED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))

        if event.event == Events.LOGIN_COMPLETED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))
        
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
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))

        if event.event == Events.REGISTRATION_METADATA_FETCHED:
            payload = {
                "event": event.event.value,
                "payload": {} 
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))

        if event.event == Events.FACILITY_CATALOG_FETCHED:
            facilityCatalog: FacilityCatalog = event.payload["facility_catalog"]
            payload = {
                "event": event.event.value,
                "payload": {
                    "facilities_by_type":facilityCatalog.facilities_by_type
                }
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))

        if event.event == Events.INSTITUTION_SELECTED:

            payload = {
                "event": event.event.value,
                "payload": {}
            }

            logging.info(f"Institution selected emitted")
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))
        
        if event.event == Events.USER_AUTHENTICATION_FAILED or event.event == Events.FETCHING_FACILITY_FAILED:

            payload = {
                "event": event.event.value,
                "payload": {}
            }

            # logging.info(f"UserAuthentication got failed")
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))
        
        if event.event == Events.JOB_FAILED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))

        if event.event == Events.REPORT_CREATED:
            payload = {
                "event": event.event.value,
                "payload": event.payload
            }
            self.event_bridge.dispatch(coroutine=self.websocket_manager.send(user_id=self.user_id,payload=payload))


