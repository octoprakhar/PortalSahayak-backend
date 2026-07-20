from disease.rules.DiseaseRule import DiseaseRule

class ReferactiveProblemsRule(DiseaseRule):
    """
    This disease will only be given to child if and only if, it is given by the user and the child is in School.
    """
    def validate(self, disease, context):
        current_count = context.current_counts.get("Referactive Problems",0)
        max_count = context.max_counts.get("Referactive Problems",9999999)

        is_current_count_less = current_count < max_count
        return disease.definition.name == context.child.diseaseName and context.institution_type == "school" and is_current_count_less