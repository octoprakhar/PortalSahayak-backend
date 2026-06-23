from disease.strategy.adding_strategies.value_adding.ValueAddingStrategy import ValueAddingStrategy
from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.repository.DiseaseRepository import DiseaseRepository

class SevereStuntingAddingStrategy(ValueAddingStrategy):
    def __init__(self):
        super().__init__()
        self.MIN_HEIGHT = 1

    def get_disease(self, repository:DiseaseRepository):
        return repository.get_by_name("Severe Stunting")
    
    
    def reach_limit(self, manipulator:DiseaseManipulator):
        """
        Need to implement till the range maybe if we reduce the height, and minimum it became 0 because 
        Severe stunting is just reducing the height.
        """
        current_height = manipulator.get_height()
        if not current_height:
            raise ValueError("Invalid height value")
        
        return current_height <= self.MIN_HEIGHT
    
    
    def adjust_value(self, child, manipulator):
        """
        I need to reduce the height and get the stunting with respect to the age.
        Note: While making stunting just remember, SAM can also be introduced. I mean 
        there can be something like stunting (introduced), and since we were reducing height
        then SAM may also come.

        For V1, let's just reduce the current value by 0.5, and just check whether stunting appeared or not, if not, then just move on. No age data 
        required, government RBSK portal will be the final source of truth
        """
        
        current_height = manipulator.get_height()
        if not current_height:
            raise ValueError("Invalid height value")
        
        manipulator.set_height(new_height=str(current_height-1))