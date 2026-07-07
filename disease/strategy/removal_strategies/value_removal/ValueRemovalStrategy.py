from abc import abstractmethod, ABC
from playwright.sync_api import Page


from disease.strategy.removal_strategies.DiseaseRemovalStrategy import DiseaseRemovalStrategy
from disease.detector.DiseaseDetector import DiseaseDetector
from services.PageSynchronizer import PageSynchronizer
from disease.models.DetectedDisease import DetectedDisease
from disease.manipulator.DiseaseManipulator import DiseaseManipulator

class ValueRemovalStrategy(DiseaseRemovalStrategy,ABC):
    def __init__(self):
        self.MAX_ATTEMPTS = 500
    
    @abstractmethod
    def reach_limit(self,manipulator:DiseaseManipulator) -> bool:
        pass

    @abstractmethod
    def adjust_value(self,manipulator: DiseaseManipulator) -> None:
        pass

    def _disease_still_present(self,page:Page,disease:DetectedDisease) -> bool:
        detector = DiseaseDetector(page=page)
        current = detector.detect()

        return any(
            d.definition.name == disease.definition.name
            for d in current
        )

    def remove(self, disease, page, synchronizer):
        attempts = 0
        manipulator = DiseaseManipulator(page, synchronizer)
        while attempts < self.MAX_ATTEMPTS:

            if not self._disease_still_present(disease=disease,page=page):
                return True

            if self.reach_limit(manipulator=manipulator):
                break

            self.adjust_value(manipulator=manipulator)

            attempts += 1

        return False

