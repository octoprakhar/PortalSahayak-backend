from playwright.sync_api import Page

from all_models.child_models import Child

from disease.detector.DiseaseDetector import DiseaseDetector
from disease.models.DetectedDisease import DetectedDisease
from disease.models.DiseaseContext import DiseaseContext
from disease.repository.DiseaseRuleRepository import DiseaseRuleRepository

from disease.strategy.removal_strategies.DiseaseRemovalStrategy import DiseaseRemovalStrategy
from disease.repository.DiseaseRemovalStrategyRepository import DiseaseRemovalStrategyRepository
from disease.manager.DiseaseCountManager import DiseaseCountManager
from disease.strategy.removal_strategies.checkbox_removal.CheckBoxRemovalStrategy import CheckboxRemovalStrategy

from services.PageSynchronizer import PageSynchronizer

class DiseaseManager:
    """
    This is the main class, that handles everything regarding diseases. 
    It orchestrated everything regarding diseases. Adding, removing, or any other thing
    """

    def __init__(self,page:Page, synchronizer: PageSynchronizer):
        self.page = page
        self.synchronizer = synchronizer
        self.disease_rule_repo = DiseaseRuleRepository()
        self.detector = DiseaseDetector(page=self.page)
        self.count_manager = DiseaseCountManager()
        self.disease_removal_repo = DiseaseRemovalStrategyRepository()
        self.managed_disease_name = self.disease_rule_repo.get_managed_disease_names()

    def manage(self, child:Child):
        """
        It manages all the diseases regarding a specific child
        """

        ## Create all disease context
        disease_context = DiseaseContext(child=child,current_counts=self.count_manager.get_current_counts(),max_counts=self.count_manager.get_max_counts())
        print(f"Made the context for the child as: \n{disease_context}")
        print("\n")
        ## 1. Detect all diseases
        
        detected_diseases : list[DetectedDisease] = self.detector.detect()
        if detected_diseases:
            print(f"Initial detected diseases are: \n{detected_diseases}")
            print("====================================")
            print("\n")
            for disease in detected_diseases:
                print(f"Now started for checking of disease : {disease.definition.name}")
                if disease.definition.name in child.diseaseName:
                    print("This disease is given by the user")
                    continue

                if disease.definition.name != child.diseaseName and disease.definition.name not in self.managed_disease_name:
                    ## This disease is wrongly selected by the portal
                    print("This disease is wrongly selected by the portal so we are trying to remove it through checkbox.")
                    removal_strategy: DiseaseRemovalStrategy = CheckboxRemovalStrategy()
                    is_disease_removed = removal_strategy.remove(disease=disease,page=self.page,synchronizer=self.synchronizer)
                    if not is_disease_removed:
                        raise Exception("Cannot remove this disease, so leaving")
                elif disease.definition.name in self.managed_disease_name:
                    print("This is a managed disease. Now checking for validation")
                    ## Check rules
                    disease_rule = self.disease_rule_repo.get_rule(disease_name=disease.definition.name)
                    print(f"Got rule for this disease as {disease_rule}")
                    if not disease_rule:
                        raise Exception("Cannot find disease rule for a managed disease")
                
                    if not disease_rule.validate(disease=disease, context=disease_context):
                        print("This disease has not cleared validation test, so getting the removal strategy")
                        removal_strategy: DiseaseRemovalStrategy = self.disease_removal_repo.get_strategy_by_disease_name(disease.definition.name)
                        print(f"Got removal strategy as {removal_strategy}")
                        is_disease_removed = removal_strategy.remove(disease=disease,page=self.page,synchronizer=self.synchronizer)
                        if not is_disease_removed:
                            raise Exception("Cannot remove this disease, so leaving")
            
                print("=========================================\n")
        
        else:
            print("Child is healthy")
                    
        
        ## TODO: Maybe we can assign a managed disease too here after deletion, if we can
        print("Checking whether should we add any disease or not.")
        ## Final output 
        final_diseases = self.detector.detect()
        print(f"Got final diseases as: {final_diseases}")
        for disease in final_diseases:
            if disease.definition.name in self.managed_disease_name:
                ## Update the count
                self.count_manager.increment(disease.definition.name)
                
        

