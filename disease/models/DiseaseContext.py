from dataclasses import dataclass
from all_models.child_models import Child

@dataclass
class DiseaseContext:
    child: Child
    current_counts: dict[str,int]
    max_counts: dict[str,int]