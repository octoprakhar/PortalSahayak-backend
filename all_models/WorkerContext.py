from dataclasses import dataclass

@dataclass
class WorkerContext:
    userName: str
    password: str