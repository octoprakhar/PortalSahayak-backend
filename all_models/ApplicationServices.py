from dataclasses import dataclass
from bridge.WorkerEventBridge import WorkerEventBridge
from websocket.WebsocketManager import WebsocketManger

from database.Database import Database
from repository.UserRepository import UserRepository

@dataclass
class ApplicationServices:
    database: Database
    user_repository: UserRepository
    event_bridge : WorkerEventBridge
    websocket_manager: WebsocketManger