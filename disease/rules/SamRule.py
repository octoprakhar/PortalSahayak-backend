from disease.rules.DiseaseRule import DiseaseRule

from utils.loaderUtils import get_age
from constants.institution_type import InstitutionType

class SamRule(DiseaseRule):
    """
    This will validate whether this child can have sam or not
    """
    def validate(self, disease, context):
        """
        SAM is only and only will be there, if sam_count is less than max count

        Otherwise False
        """
        child_disease = context.child.diseaseName
        current_count = context.current_counts.get("SAM/Severe Thinness/SUW",0)
        max_count = context.max_counts.get("SAM/Severe Thinness/SUW",9999999)

        is_current_count_less = current_count < max_count

        return not child_disease.strip() and is_current_count_less and context.institution_type != InstitutionType.SCHOOL
