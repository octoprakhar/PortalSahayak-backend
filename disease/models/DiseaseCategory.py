from enum import Enum

class DiseaseCategory(Enum):
    """
    All the diseases can be classified in these categories that will be provided
    in the subsequent future for each disease.
    """
    DEFECTS_AT_BIRTH = "A"
    DEFICIENCIES = "B"
    CHILDHOOD_DISEASES = "C"
    DEVELOPMENTAL_DELAY = "D"
    OTHERS = "E"
    ADOLSCENT_HEALTH_CONCERNS = "F"