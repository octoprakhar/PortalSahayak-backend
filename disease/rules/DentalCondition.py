from disease.rules.DiseaseRule import DiseaseRule
from utils.loaderUtils import get_age

class DentalConditionRule(DiseaseRule):
    def validate(self, disease, context):
        current = context.current_counts.get("Dental Conditions",0)
        max_count = context.max_counts.get("Dental Conditions",99999)

        age = get_age(context.child.dob)
        if not age:
            return False

        # return current < max_count and age > 5 and disease.definition.name == context.child.diseaseName
        return age > 5 and disease.definition.name == context.child.diseaseName