import math

from disease.config.DiseaseQuotaConfig import DiseaseQuotaConfig

from disease.manager.DiseaseCountManager import DiseaseCountManager

class DiseaseCountFactory:
    """
    This class will take the configuration file for all disease quotas and 
    returns max_count of each disease. 
    In simple words it takes total children, configuration file as input and give
    DiseaseCountManager as the output.
    """

    @staticmethod
    def create(max_len: int) -> DiseaseCountManager:
        max_counts = {
            disease: min(
                math.ceil(percentage * max_len),
                max_len
            )
            for disease, percentage in DiseaseQuotaConfig.QUOTAS.items()
        }
        return DiseaseCountManager(max_counts=max_counts)