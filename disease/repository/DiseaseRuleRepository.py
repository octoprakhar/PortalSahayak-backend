from disease.rules.DiseaseRule import DiseaseRule
from disease.rules.SamRule import SamRule
from disease.rules.DentalCondition import DentalConditionRule
from disease.rules.SkinConditionRule import SkinConditionRule
from disease.rules.SevereStuntingRule import SevereStuntingRule
from disease.rules.MildAnaemiaRule import MildAnaemiaRule
from disease.rules.ModerateAnaemiaRule import ModerateAnaemiaRule
from disease.rules.SkinConditionsNotLeprosyRule import SkinConditionsNotLeprosyRule

class DiseaseRuleRepository:
    """
    All the disease, that are target diseases, there names and rules are mapped here.

    Target diseases are those diseases, whose rules are written.
    """
    def __init__(self):
        self.rules = {
            "SAM/Severe Thinness/SUW": SamRule(),
            "Severe Stunting": SevereStuntingRule(),
            "Mild Anaemia": MildAnaemiaRule(),
            "Moderate Anaemia": ModerateAnaemiaRule(),
            "Skin Conditions": SkinConditionRule(),
            "Dental Conditions": DentalConditionRule(),
            "Skin Condtions Not Leprosy": SkinConditionsNotLeprosyRule()
                      }
        
    def get_rule(self, disease_name: str) -> DiseaseRule | None:
        return self.rules.get(disease_name)
    
    def get_managed_disease_names(self):
        return list(self.rules.keys())