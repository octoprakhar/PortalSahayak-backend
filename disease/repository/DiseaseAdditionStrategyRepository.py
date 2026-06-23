from disease.strategy.adding_strategies.checkbox_adding.DentalDiseaseAddingStrategy import DentalDiseaseAdditionStrategy
from disease.strategy.adding_strategies.checkbox_adding.SkinDiseaseAdditionStrategy import SkinDiseaseAdditionStrategy
from disease.strategy.adding_strategies.value_adding.SevereStuntingAddingStrategy import SevereStuntingAddingStrategy
from disease.strategy.adding_strategies.value_adding.MildAnaemiaAddingStrategy import MildAnaemiaAddingStrategy
from disease.strategy.adding_strategies.value_adding.ModerateAnaemiaAddingStrategy import ModerateAnaemiaAddingStrategy
from disease.strategy.adding_strategies.DiseaseAdditionStrategy import DiseaseAdditionStrategy


class DiseaseAdditionStrategyRepository:
    """
    These number of diseases I should add for extra, if I any of these are not present already to a child. 
    """
    def __init__(self):

        self.disease_addition_strategies = {
            "Skin Conditions":
                lambda: SkinDiseaseAdditionStrategy(),
            "Dental Conditions":
                lambda: DentalDiseaseAdditionStrategy(),
            "Severe Stunting":
                lambda: SevereStuntingAddingStrategy(),
            "Moderate Anaemia":
                lambda: ModerateAnaemiaAddingStrategy(),
            "Mild Anaemia":
                lambda: MildAnaemiaAddingStrategy(),
        }
        
    def get_strategy_by_disease_name(self, disease_name) -> DiseaseAdditionStrategy | None:
        """
        Give adding strategy for the disease, and returns none, for a specific disease if not present. Reason behind none is that 
        there is no default disease must be there to add. 
        """
        strategy_factory = self.disease_addition_strategies.get(
            disease_name
        )

        if not strategy_factory:
            return None

        return strategy_factory()
    
    def get_all_disease_name_for_adding_strategy(self)->list[str]:
        return list(self.disease_addition_strategies.keys())