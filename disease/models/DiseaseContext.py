from dataclasses import dataclass
from all_models.child_models import Child
from constants.institution_type import InstitutionType

@dataclass
class DiseaseContext:
    child: Child
    institution_type: InstitutionType
    current_counts: dict[str,int]
    max_counts: dict[str,int]