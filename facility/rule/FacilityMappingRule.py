from disease.models.DetectedDisease import DetectedDisease
from facility.constants.FacilityType import FacilityType

class FacilityMappingRule:
    """
    It will give us the enum value for the facility that for the disease it is used
    """

    def get_facility_type_for_disease(self,disease:DetectedDisease) -> FacilityType:
        target_diseases = ["Severe Stunting", "Mild Anaemia", "Moderate Anaemia", "Skin Conditions", "Dental Conditions", "Skin Condtions Not Leprosy"]
        if disease.definition.name == "SAM/Severe Thinness/SUW":
            return FacilityType.NRC
        if disease.definition.name == "Referactive Problems":
            return FacilityType.DISTRICT
        if disease.definition.name in target_diseases:
            return FacilityType.BLOCK
        
        return FacilityType.DISTRICT