from disease.strategy.removal_strategies.value_removal.ValueRemovalStrategy import ValueRemovalStrategy


class SamValueRemovalStrategy(ValueRemovalStrategy):
    def __init__(self):
        super().__init__()
        self.MAX_WEIGHT = 18
        self.MAX_HEIGHT = 110

    def _is_height_reached_limit(self,current_height: float) -> bool:
        return current_height > self.MAX_HEIGHT
    
    def _is_weight_reached_limit(self,current_weight: float) -> bool:
        return current_weight > self.MAX_WEIGHT


    def adjust_value(self, manipulator):
        current_height = manipulator.get_height()
        current_weight = manipulator.get_weight()
        if not self._is_height_reached_limit(current_height=current_height) and not self._is_weight_reached_limit(current_weight=current_weight):
            ## Update both
            manipulator.set_weight(str(current_weight + 0.5))
            manipulator.set_height(str(current_height + 0.5))
        elif self._is_height_reached_limit(current_height=current_height):
            ## Update the weight
            manipulator.set_weight(str(current_weight + 0.5))
        else:
            ## Update the height
            manipulator.set_height(str(current_height + 0.5))
            
    
    def reach_limit(self, manipulator):
        current_height = manipulator.get_height()
        current_weight = manipulator.get_weight()

        if not current_height or not current_weight:
            raise ValueError("Height or weight is invalid")
        
        return self._is_height_reached_limit(current_height=current_height) and self._is_weight_reached_limit(current_weight=current_weight)