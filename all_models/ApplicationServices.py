from dataclasses import dataclass
from bridge.WorkerEventBridge import WorkerEventBridge
from websocket.WebsocketManager import WebsocketManger

from database.Database import Database
from repository.UserRepository import UserRepository
from repository.JobRepository import JobRepository

@dataclass
class ApplicationServices:
    database: Database
    user_repository: UserRepository
    job_repository: JobRepository
    event_bridge : WorkerEventBridge
    websocket_manager: WebsocketManger