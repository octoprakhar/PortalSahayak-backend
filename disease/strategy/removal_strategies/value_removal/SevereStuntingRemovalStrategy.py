from disease.strategy.removal_strategies.value_removal.ValueRemovalStrategy import ValueRemovalStrategy
from disease.manipulator.DiseaseManipulator import DiseaseManipulator

class SevereStuntingRemovalStrategy(ValueRemovalStrategy):
    def __init__(self):
        super().__init__()
        self.MAX_HEIGHT = 110
    def reach_limit(self, manipulator:DiseaseManipulator)-> bool:
        current_height = manipulator.get_height()
        if not current_height:
            raise ValueError("Cannot run Severe stunting removal because of invalid height")
        
        return current_height >= self.MAX_HEIGHT
    
    def adjust_value(self, manipulator:DiseaseManipulator)-> None:
        current_height = manipulator.get_height()
        if not current_height:
            raise ValueError("Cannot run Severe stunting removal because of invalid height")
        
        manipulator.set_height(str(current_height+0.5))
