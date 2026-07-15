from disease.rules.DiseaseRule import DiseaseRule
from utils.loaderUtils import get_age

class SkinConditionRule(DiseaseRule):
    def validate(self, disease, context):
        current = context.current_counts.get("Skin Conditions",0)
        max_count = context.max_counts.get("Skin Conditions",99999)
        age = get_age(context.child.dob)
        return current < max_count and age < 6