from dataclasses import dataclass

from disease.models.DiseaseDefinition import DiseaseDefinition
from disease.models.DiseaseSource import DiseaseSource

@dataclass
class DetectedDisease:
    """
    The disease detector will give the list of diseases in this format
    """
    definition: DiseaseDefinition
    source: DiseaseSource