from disease.rules.DiseaseRule import DiseaseRule

class SevereStuntingRule(DiseaseRule):
    """
    RUles to validate severe stunting
    """
    def validate(self, disease, context):
        current = context.current_counts.get("Severe Stunting",0)
        max_count = context.max_counts.get("Severe Stunting",99999)

        return current < max_count