from abc import ABC,abstractmethod
from playwright.sync_api import Page

from disease.strategy.adding_strategies.DiseaseAdditionStrategy import DiseaseAdditionStrategy
from all_models.child_models import Child
from services.PageSynchronizer import PageSynchronizer
from disease.repository.DiseaseRepository import DiseaseRepository
from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.detector.DiseaseDetector import DiseaseDetector
from disease.models.DiseaseDefinition import DiseaseDefinition

class ValueAddingStrategy(DiseaseAdditionStrategy,ABC):
    def __init__(self):
        super().__init__()
        self.MAX_ATTEMPTS = 50
    
    @abstractmethod
    def reach_limit(self,manipulator: DiseaseManipulator) -> bool:
        pass

    @abstractmethod
    def adjust_value(self, child:Child, manipulator: DiseaseManipulator)-> None:
        pass

    @abstractmethod
    def get_disease(self,repository: DiseaseRepository) -> DiseaseDefinition:
        pass

    def _is_disease_present(self, page:Page, disease:DiseaseDefinition)-> bool:
        
        detector = DiseaseDetector(page=page)
        current = detector.detect()

        return any(
            d.definition.name == disease.name
            for d in current
        )
        

    def add(self, child:Child, page:Page, synchronizer:PageSynchronizer, repository:DiseaseRepository) -> bool:
        attempts = 0
        manipulator = DiseaseManipulator(page=page,synchronizer=synchronizer)
        disease = self.get_disease(repository=repository)


    

        while attempts < self.MAX_ATTEMPTS:

            if self._is_disease_present(page=page, disease=disease):

                return True
            
            if self.reach_limit(manipulator=manipulator):
                break

            self.adjust_value(child=child,manipulator=manipulator)
            attempts += 1


        
        return False

        