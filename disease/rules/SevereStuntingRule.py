from disease.rules.DiseaseRule import DiseaseRule

class SevereStuntingRule(DiseaseRule):
    """
    RUles to validate severe stunting
    """
    def validate(self, disease, context):
        
        child_disease = context.child.diseaseName
        current = context.current_counts.get("Severe Stunting",0)
        max_count = context.max_counts.get("Severe Stunting",99999)

        is_current_count_less = current < max_count

        return not child_disease.strip() and is_current_count_less