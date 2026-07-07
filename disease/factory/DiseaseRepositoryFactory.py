from all_models.child_models import Child

from disease.models.DiseaseDefinition import DiseaseDefinition
from utils.loaderUtils import get_age

from disease.repository.DiseaseRepository import DiseaseRepository
from disease.repository.AdolscentBoysDiseaseRepository import AdolscentBoysDiseaseRepository
from disease.repository.AdolscentGirlsDiseaseRepository import AdolscentGirlDiseaseRepository
from disease.repository.DiseaseRepositoryAbstract import DiseaseRepositoryAbstract
from disease.repository.CombinedDiseaseRepository import CombinedDiseaseRepository

class DiseaseRepositoryFactory:
    """
    This factory will give us the list [DiseaseDefinition] for a particular child based of age, gender etc.
    """
    def __init__(self):
        self.base_repo = DiseaseRepository()
        self.adolscent_boy_repo = AdolscentBoysDiseaseRepository()
        self.adolscent_girl_repo = AdolscentGirlDiseaseRepository()

    def get_disease_repo(self,child:Child) -> DiseaseRepositoryAbstract:
        if get_age(child.dob) <10:
            return CombinedDiseaseRepository(repositories=[self.base_repo])
        
        if get_age(child.dob) >= 10 and get_age(child.dob) < 19:
            if child.gender.lower() == "male":
                return CombinedDiseaseRepository(repositories=[self.base_repo,self.adolscent_boy_repo])
            else:
                return CombinedDiseaseRepository(repositories=[self.base_repo,self.adolscent_girl_repo]) 
        
        return CombinedDiseaseRepository(
            repositories=[self.base_repo]
        )