from disease.strategy.adding_strategies.value_adding.ValueAddingStrategy import ValueAddingStrategy

from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.repository.DiseaseRepository import DiseaseRepository

class MildAnaemiaAddingStrategy(ValueAddingStrategy):
    def __init__(self):
        super().__init__()
        self.MIN_HB = 4

    def reach_limit(self, manipulator: DiseaseManipulator):
        current_hb = manipulator.get_hb()
        if not current_hb:
            raise ValueError("Invalid HB value")
        
        return current_hb <= self.MIN_HB
    
    def get_disease(self, repository: DiseaseRepository):
        return repository.get_by_name("Mild Anaemia")
    
    def adjust_value(self, child, manipulator: DiseaseManipulator):
        current_hb = manipulator.get_hb()
        if not current_hb:
            raise ValueError("Invalid HB value")
        
        manipulator.set_hb(str(current_hb - 0.5))