from abc import ABC,abstractmethod

from disease.models.DiseaseDefinition import DiseaseDefinition

class DiseaseRepositoryAbstract(ABC):

    @abstractmethod
    def get_by_name(self,name:str)-> DiseaseDefinition:
        """
        Pass the name of the disease to get all the diseases
        """
    
    @abstractmethod
    def get_by_code(self,code:str):
        pass