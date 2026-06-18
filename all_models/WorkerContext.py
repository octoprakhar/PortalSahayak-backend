from dataclasses import dataclass

@dataclass
class WorkerContext:
    userName: str
    password: str
    address: str
    mobile_number: str
    planned_date: str
    uploaded_file_path: str