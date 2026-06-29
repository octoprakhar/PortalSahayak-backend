from dataclasses import dataclass
from bridge.WorkerEventBridge import WorkerEventBridge
from websocket.WebsocketManager import WebsocketManger

@dataclass
class ApplicationServices:
    event_bridge : WorkerEventBridge
    websocket_manager: WebsocketManger