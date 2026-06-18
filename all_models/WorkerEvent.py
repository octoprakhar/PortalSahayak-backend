from dataclasses import dataclass

from constants.Events import Events

@dataclass
class WorkerEvent:
    event: Events
    job_id: str
    payload: dict