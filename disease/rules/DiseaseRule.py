from abc import abstractmethod,ABC
from disease.models.DetectedDisease import DetectedDisease
from disease.models.DiseaseContext import DiseaseContext

class DiseaseRule(ABC):
    @abstractmethod
    def validate(self, disease: DetectedDisease, context:DiseaseContext) -> bool:
        """
        It will just validate the disease with the given context. whether we can insert it or not
        """
        pass