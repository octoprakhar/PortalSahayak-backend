import logging

from disease.strategy.removal_strategies.value_removal.ValueRemovalStrategy import ValueRemovalStrategy
from disease.manipulator.DiseaseManipulator import DiseaseManipulator

class MicrocephelyRemovalStrategy(ValueRemovalStrategy):

    def __init__(self):
        super().__init__()
        self.MAX_HEAD_CIRCUMFERENCE = 51
    def reach_limit(self, manipulator:DiseaseManipulator):
        current_head_circumference = manipulator.get_head_circumference()
        if not current_head_circumference:
            logging.error(f"Got head circumference value as : {current_head_circumference} and of type : {type(current_head_circumference)}")
            raise ValueError("Invalid value of head circumference")
        return current_head_circumference >= self.MAX_HEAD_CIRCUMFERENCE
        
    
    def adjust_value(self, manipulator:DiseaseManipulator):
        current_head_circumference = manipulator.get_head_circumference()
        if not current_head_circumference:
            logging.error(f"Got head circumference value as : {current_head_circumference} and of type : {type(current_head_circumference)}")
            raise ValueError("Invalid value of head circumference")
        
        manipulator.set_head_circumference(str(current_head_circumference+1))