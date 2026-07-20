from disease.strategy.adding_strategies.value_adding.ValueAddingStrategy import ValueAddingStrategy

from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.repository.DiseaseRepository import DiseaseRepository

class ReferactiveProblemsAdditionStrategy(ValueAddingStrategy):
    def __init__(self):
        super().__init__()
        self.target_vision_left = "6/12"

    def reach_limit(self, manipulator: DiseaseManipulator):
        vision_left = manipulator.get_vision_left()
        if not vision_left:
            raise ValueError("Invalid vision left value")
        
        return vision_left == self.target_vision_left
    
    def get_disease(self, repository: DiseaseRepository):
        return repository.get_by_name("Referactive Problems")
    
    def adjust_value(self, child, manipulator: DiseaseManipulator):
        
        manipulator.set_vision_left(vision=self.target_vision_left)