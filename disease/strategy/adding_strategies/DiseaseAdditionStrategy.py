from abc import ABC,abstractmethod
from playwright.sync_api import Page

from all_models.child_models import Child
from services.PageSynchronizer import PageSynchronizer
from disease.repository.DiseaseRepository import DiseaseRepository

class DiseaseAdditionStrategy(ABC):
    
    @abstractmethod
    def add(self, child:Child, page:Page, synchronizer: PageSynchronizer,repository: DiseaseRepository) -> bool:
        """
        This method helps in adding disease. It took child because for some disease to add,
        we need to pass specific value, for specific child details like (age).
        """
        pass
