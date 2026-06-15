from dataclasses import dataclass

from constants.institution_type import InstitutionType

@dataclass
class InstitutionData:
    institution_plan_id: int
    institution_name: str
    institution_type: InstitutionType
    planned_date : str
    