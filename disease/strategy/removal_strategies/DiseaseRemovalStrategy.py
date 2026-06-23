from abc import ABC,abstractmethod
from playwright.sync_api import Page


from disease.models.DetectedDisease import DetectedDisease
from services.PageSynchronizer import PageSynchronizer

class DiseaseRemovalStrategy(ABC):
    @abstractmethod
    def remove(self, disease: DetectedDisease, page: Page,synchronizer: PageSynchronizer) -> bool:
        """
        Any removal strategy must complete this method and tell how to remove that disease
        """