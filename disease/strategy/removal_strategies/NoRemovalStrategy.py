from disease.strategy.removal_strategies.DiseaseRemovalStrategy import DiseaseRemovalStrategy

class NoRemovalStrategy(DiseaseRemovalStrategy):
    """
    This class will be used as the default if for any disease removal strategy is not shown
    """
    def remove(self, disease, page, synchronizer):
        raise NotImplementedError(
            f"No removal strategy registered for {disease.definition.name}"
        )