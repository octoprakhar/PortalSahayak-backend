from dataclasses import dataclass
from bridge.WorkerEventBridge import WorkerEventBridge
from websocket.WebsocketManager import WebsocketManger

from database.Database import Database
from repository.UserRepository import UserRepository
from repository.JobRepository import JobRepository
from repository.ReportRepository import ReportRepository

@dataclass
class ApplicationServices:
    database: Database
    user_repository: UserRepository
    job_repository: JobRepository
    report_repository: ReportRepository
    event_bridge : WorkerEventBridge
    websocket_manager: WebsocketManger