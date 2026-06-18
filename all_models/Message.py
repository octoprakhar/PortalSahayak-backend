from dataclasses import dataclass

from constants.Commands import Commands

@dataclass
class Message:
    job_id: str
    command: Commands
    payload: dict