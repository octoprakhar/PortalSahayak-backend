import random

from disease.strategy.removal_strategies.value_removal.ValueRemovalStrategy import ValueRemovalStrategy
from disease.manipulator.DiseaseManipulator import DiseaseManipulator

class AnaemiaRemovalStrategy(ValueRemovalStrategy):
    """
    It will work for both Moderate and Mild anaemia. We just need to choose any value between 12-14 to put on it
    """
    def reach_limit(self, manipulator:DiseaseManipulator):
        """
        Just check if current hb is above 12 and then also it is showing anaemia it's the portal's problem
        """
        current_hb = manipulator.get_hb()
        if not current_hb:
            raise ValueError('Invalid hb is given')
        return current_hb >= 13
    
    def adjust_value(self, manipulator:DiseaseManipulator):
        """
        Just set a random value between 12-14
        """
        currected_hb = round(random.uniform(13, 14), 1)
        manipulator.set_hb(str(currected_hb))
        
        