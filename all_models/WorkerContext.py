from dataclasses import dataclass

from all_models.InstitutionData import InstitutionData

@dataclass
class WorkerContext:
    userName: str
    password: str
    address: str
    mobile_number: str
    planned_date: str
    uploaded_file_path: str = None
    institution_data: InstitutionData = None
