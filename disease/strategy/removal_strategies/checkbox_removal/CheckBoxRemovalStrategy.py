from disease.detector.DiseaseDetector import DiseaseDetector
from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.strategy.removal_strategies.DiseaseRemovalStrategy import DiseaseRemovalStrategy

from disease.models.DetectedDisease import DetectedDisease

class CheckboxRemovalStrategy(DiseaseRemovalStrategy):
    def remove(self, disease, page, synchronizer) -> bool:

        detector = DiseaseDetector(page=page)
        manipulator = DiseaseManipulator(page=page, synchronizer=synchronizer)
        try_counter = 0
        print(f"Got detected lists of diseases as {detector.detect()}")


        while try_counter < 5:
            current_diseases = detector.detect()  
            if disease not in current_diseases:
                return True
            if disease in current_diseases:
                manipulator.uncheck_box(disease=disease.definition)
                print(f"After try: {try_counter + 1} is disease there : {current_diseases}") 
                try_counter += 1
        
        return disease in detector.detect()

