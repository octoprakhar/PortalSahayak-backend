from disease.rules.DiseaseRule import DiseaseRule
from utils.loaderUtils import get_age

class ModerateAnaemiaRule(DiseaseRule):
    def validate(self, disease, context):
        current = context.current_counts.get("Moderate Anaemia",0)
        max_count = context.max_counts.get("Moderate Anaemia",99999)

        age = get_age(context.child.dob)
        if not age:
            return False
        
        return current < max_count and age > 1