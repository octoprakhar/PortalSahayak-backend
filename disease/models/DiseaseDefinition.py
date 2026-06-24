from dataclasses import dataclass

from disease.models.DiseaseCategory import DiseaseCategory

@dataclass
class DiseaseQuestion:
    code: str
    text: str

@dataclass
class DiseaseDefinition:
    """
    This class will try to model what is a disease. Like what things we need to say a thing is a disease.
    """
    name: str
    code: str | None ## None because it might be an 'Others' disease so portal doesn't have a code for it.
    category: DiseaseCategory
    questions: list[DiseaseQuestion]