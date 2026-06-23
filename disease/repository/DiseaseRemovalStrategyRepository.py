from playwright.sync_api import Page

from disease.strategy.removal_strategies.checkbox_removal.CheckBoxRemovalStrategy import CheckboxRemovalStrategy
from disease.strategy.removal_strategies.value_removal.SamValueRemovalStrategy import SamValueRemovalStrategy
from disease.strategy.removal_strategies.DiseaseRemovalStrategy import DiseaseRemovalStrategy
from disease.strategy.removal_strategies.NoRemovalStrategy import NoRemovalStrategy

from services.PageSynchronizer import PageSynchronizer

class DiseaseRemovalStrategyRepository:
    """
    All removal strategies are stored here, for all planned diseases, if not present for specific disease
    that means it is checkbox removal disease
    """

    def __init__(self):

        self.disease_removal_strategies = {
            "SAM/Severe Thinness/SUW":
                lambda: SamValueRemovalStrategy(),

            "DEFAULT":
                lambda: NoRemovalStrategy()
        }
        
    def get_strategy_by_disease_name(self, disease_name):
        strategy_factory = self.disease_removal_strategies.get(
            disease_name,
            self.disease_removal_strategies["DEFAULT"]
        )

        return strategy_factory()