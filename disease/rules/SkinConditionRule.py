from disease.rules.DiseaseRule import DiseaseRule

class SkinConditionRule(DiseaseRule):
    def validate(self, disease, context):
        current = context.current_counts.get("Skin Conditions",0)
        max_count = context.max_counts.get("Skin Conditions",99999)
        return current < max_count