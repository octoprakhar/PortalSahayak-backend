from copy import deepcopy


from disease.strategy.adding_strategies.checkbox_adding.CheckboxAdditionStrategy import CheckboxAdditionStrategy
from disease.models.DiseaseDefinition import DiseaseQuestion


class SkinDiseaseNotLeprosyAdditionStrategy(CheckboxAdditionStrategy):
    def get_disease(self, repository):
        return repository.get_by_name("Skin Condtions Not Leprosy")