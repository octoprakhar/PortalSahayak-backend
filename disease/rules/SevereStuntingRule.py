from disease.rules.DiseaseRule import DiseaseRule
from utils.loaderUtils import get_age


class SevereStuntingRule(DiseaseRule):
    """
    RUles to validate severe stunting
    """
    def validate(self, disease, context):
        
        child_disease = context.child.diseaseName
        current = context.current_counts.get("Severe Stunting",0)
        max_count = context.max_counts.get("Severe Stunting",99999)
        age = get_age(context.child.dob)

        is_current_count_less = current < max_count

        return not child_disease.strip() and is_current_count_less and age < 6