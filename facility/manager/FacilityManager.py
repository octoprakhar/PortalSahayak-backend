from playwright.sync_api import Page

from disease.models.DetectedDisease import DetectedDisease
from facility.constants.FacilityType import FacilityType

from facility.rule.FacilityMappingRule import FacilityMappingRule
from facility.manipulator.FacilityManipulator import FacilityManipulator

from facility.model.ReferralDecision import ReferralDecision
from services.PageSynchronizer import PageSynchronizer

class FacilityManager:

    def __init__(self,selected_mapping: dict[str,str], page:Page, mapping_rules: FacilityMappingRule, synchronizer: PageSynchronizer):
        self.page = page
        self.mapping_rule:FacilityMappingRule = mapping_rules
        self.selected_mapping = selected_mapping ## User selected mapping of facilityType: facilityName
        self.facility_manipulator = FacilityManipulator(page=page,synchronizer=synchronizer)

    def manage(self,detected_diseases: list[DetectedDisease]):
        """
        It will map each disease with it's detected disease by taking the rule
        """
        for disease in detected_diseases:
            ## Get mapping rule for this disease
            facility_type: FacilityType = self.mapping_rule.get_facility_type_for_disease(disease = disease)

            if facility_type == FacilityType.DISTRICT and self.selected_mapping[FacilityType.DEIC]:
                ## if facility type is given district, and mapping has deic present
                facility_type = FacilityType.DEIC

            ## Get facility name of that facility type
            facility_name = self.selected_mapping.get(facility_type.value)
            if not facility_name:
                raise RuntimeError(f"No facility configured for {facility_type.value}")
            
            ## Select that specific facility name and type for that disease
            self.facility_manipulator.select_facility_type_and_name(referral_decision=ReferralDecision(disease_name=disease.definition.name,facility_type=facility_type,facility_name=facility_name))
            

