from disease.strategy.removal_strategies.value_removal.ValueRemovalStrategy import ValueRemovalStrategy
from disease.manipulator.DiseaseManipulator import DiseaseManipulator

class ReferactiveProblemsRemovalStrategy(ValueRemovalStrategy):

    def __init__(self):
        super().__init__()
        self.target_left_vision = "6/6"
        self.target_right_vision = "6/6"
    def reach_limit(self, manipulator:DiseaseManipulator):
        curr_left_vision = manipulator.get_vision_left()
        curr_right_vision = manipulator.get_vision_right()
        if not curr_left_vision or not curr_right_vision:
            raise ValueError("Invalid vision values")
        return curr_left_vision == self.target_left_vision and curr_right_vision == self.target_right_vision
        
    
    def adjust_value(self, manipulator:DiseaseManipulator):
        manipulator.set_vision_left(vision=self.target_left_vision)
        manipulator.set_vision_right(vision=self.target_right_vision)