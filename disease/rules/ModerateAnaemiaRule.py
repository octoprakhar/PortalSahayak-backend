from disease.rules.DiseaseRule import DiseaseRule

class ModerateAnaemiaRule(DiseaseRule):
    def validate(self, disease, context):
        current = context.current_counts.get("Moderate Anaemia",0)
        max_count = context.max_counts.get("Moderate Anaemia",99999)

        return current < max_count