from abc import ABC,abstractmethod
from playwright.sync_api import Page

from disease.strategy.adding_strategies.DiseaseAdditionStrategy import DiseaseAdditionStrategy
from all_models.child_models import Child
from disease.models.DiseaseDefinition import DiseaseDefinition
from disease.models.DiseaseCategory import DiseaseCategory
from services.PageSynchronizer import PageSynchronizer
from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.repository.DiseaseRepository import DiseaseRepository

class CheckboxAdditionStrategy(DiseaseAdditionStrategy,ABC):

    @abstractmethod
    def get_disease(self,repository:DiseaseRepository) -> DiseaseDefinition:
        pass

    def add(self, child, page, synchronizer, repository)-> bool:
        disease = self.get_disease(repository=repository)

        ## Call the manipulator
        manipulator = DiseaseManipulator(page=page,synchronizer=synchronizer)
        try:
            manipulator.click_check_box(disease=disease)
            return True
        except Exception:
            return False
