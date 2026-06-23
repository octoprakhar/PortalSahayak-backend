from disease.rules.DiseaseRule import DiseaseRule

class MildAnaemiaRule(DiseaseRule):
    def validate(self, disease, context):
        current = context.current_counts.get("Mild Anaemia",0)
        max_count = context.max_counts.get("Mild Anaemia",99999)
        
        return current < max_count