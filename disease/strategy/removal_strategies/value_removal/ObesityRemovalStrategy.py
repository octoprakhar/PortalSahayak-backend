from disease.strategy.removal_strategies.value_removal.ValueRemovalStrategy import ValueRemovalStrategy
from disease.manipulator.DiseaseManipulator import DiseaseManipulator

class ObesityRemovalStrategy(ValueRemovalStrategy):
    def __init__(self):
        super().__init__()
        self.MIN_WEIGHT = 1
        self.MAX_HEIGHT = 175

    def reach_limit(self, manipulator:DiseaseManipulator):
        curr_weight = manipulator.get_weight()
        curr_height = manipulator.get_height()

        if not curr_height or not curr_weight:
            raise ValueError("Invalid weight or height")
        
        return curr_weight < self.MIN_WEIGHT and curr_height >= self.MAX_HEIGHT
    
    def adjust_value(self, manipulator:DiseaseManipulator):
        current_height = manipulator.get_height()
        current_weight = manipulator.get_weight()

        if (
            current_weight > self.MIN_WEIGHT
            and current_height < self.MAX_HEIGHT
        ):
            manipulator.set_weight(str(current_weight - 0.5))
            manipulator.set_height(str(current_height + 0.5))

        elif current_weight > self.MIN_WEIGHT:
            manipulator.set_weight(str(current_weight - 0.5))

        elif current_height < self.MAX_HEIGHT:
            manipulator.set_height(str(current_height + 0.5))