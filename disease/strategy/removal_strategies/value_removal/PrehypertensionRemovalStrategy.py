from disease.strategy.removal_strategies.value_removal.ValueRemovalStrategy import ValueRemovalStrategy
from disease.manipulator.DiseaseManipulator import DiseaseManipulator

class PrehypertensionRemovalStrategy(ValueRemovalStrategy):
    
    def reach_limit(self, manipulator:DiseaseManipulator)-> bool:
        current_bp = manipulator.get_bp()
        if not current_bp:
            raise ValueError("Cannot run Severe stunting removal because of invalid bp")
        
        return current_bp == ""
    
    def adjust_value(self, manipulator:DiseaseManipulator)-> None:
        current_bp = manipulator.get_bp()
        if not current_bp:
            raise ValueError("Cannot run Severe stunting removal because of invalid height")
        
        manipulator.remove_bp()