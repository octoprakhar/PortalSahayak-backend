from playwright.sync_api import Page
import logging

from all_models.child_models import Child

from disease.detector.DiseaseDetector import DiseaseDetector
from disease.models.DetectedDisease import DetectedDisease
from disease.models.DiseaseContext import DiseaseContext
from disease.repository.DiseaseRuleRepository import DiseaseRuleRepository

from disease.strategy.removal_strategies.DiseaseRemovalStrategy import DiseaseRemovalStrategy
from disease.repository.DiseaseRemovalStrategyRepository import DiseaseRemovalStrategyRepository
from disease.manager.DiseaseCountManager import DiseaseCountManager
from disease.strategy.removal_strategies.checkbox_removal.CheckBoxRemovalStrategy import CheckboxRemovalStrategy
from disease.repository.DiseaseAdditionStrategyRepository import DiseaseAdditionStrategyRepository
from disease.repository.DiseaseRepository import DiseaseRepository
from disease.models.DiseaseSource import DiseaseSource
from disease.models.DiseaseDefinition import DiseaseDefinition
from disease.models.DiseaseCategory import DiseaseCategory
from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.strategy.adding_strategies.DiseaseAdditionStrategy import DiseaseAdditionStrategy
from disease.factory.DiseaseRepositoryFactory import DiseaseRepositoryFactory
from disease.repository.DiseaseVariantRegistry import DiseaseVariantRegistry

from constants.institution_type import InstitutionType
from services.PageSynchronizer import PageSynchronizer

from utils.loaderUtils import get_age

class DiseaseManager:
    """
    This is the main class, that handles everything regarding diseases. 
    It orchestrated everything regarding diseases. Adding, removing, or any other thing
    """

    def __init__(self,page:Page, synchronizer: PageSynchronizer, count_manager: DiseaseCountManager):
        self.page = page
        self.synchronizer = synchronizer
        self.disease_rule_repo = DiseaseRuleRepository()
        self.detector = DiseaseDetector(page=self.page)
        self.count_manager = count_manager
        self.disease_removal_repo = DiseaseRemovalStrategyRepository()
        self.disease_addition_repo = DiseaseAdditionStrategyRepository()
        self.disease_variant_registry = DiseaseVariantRegistry()
        self.disease_factory = DiseaseRepositoryFactory()
        self.full_diseases_repo = None
        self.managed_disease_name = self.disease_rule_repo.get_managed_disease_names()


    def _select_user_given_disease(self,disease_name: str, child: Child, disease_context: DiseaseContext)-> None:
        """
        Using manipulator it will try selecting user's disease
        """

        ## 1. Get full disease from disease_name
        full_disease = self.full_diseases_repo.get_by_name(name=disease_name)
        ## NOw let's make the manipulator and pass it the disease
        manipulator = DiseaseManipulator(page=self.page,synchronizer=self.synchronizer)

        if not full_disease:
            ## It means disease is not default disease it is from others
            ## So we need to make disease definition by ourselves
            full_disease = DiseaseDefinition(name=disease_name,category=DiseaseCategory.OTHERS,code=None,questions=[])
            # print(f"This is the other's category disease of the user. So we made the disease.")
            # print(f"Got full disease as {full_disease}")
            manipulator.select_others_disease(disease=full_disease)
        else:
            # print(f"Got full disease as {full_disease}")
            ## First check if addition rule is present for that user disease. It might be just disease that could be selected by value
            addition_strategy = self.disease_addition_repo.get_strategy_by_disease_name(disease_name=disease_name)
            if not addition_strategy:
                # Then try checkbox clicking
                logging.error("Can't found adding strategy for user selected disease. Now trying to click checkbox")
                manipulator.click_check_box(disease=full_disease)

            is_disease_added = addition_strategy.add(child=child,page=self.page,synchronizer=self.synchronizer,repository=self.full_diseases_repo)
            if not is_disease_added:
                logging.error(f"Even though after getting addintion strategy for the user given disease disease: {disease_name}, we can't add it.")
            else:
                logging.info(f"Added user given disease succesfully using addition strategy: {disease_name}.")



    def manage(self, child:Child, institution_type: InstitutionType) -> list[DetectedDisease]:
        """
        It manages all the diseases regarding a specific child
        """

        # self.log_bp("Starting manage() method: ")

        ## Intitialize and get full disease repo
        self.full_diseases_repo = self.disease_factory.get_disease_repo(child=child)

        # print("Disease Manager is called.")

        ## Create all disease context
        disease_context = DiseaseContext(child=child,current_counts=self.count_manager.get_current_counts(),max_counts=self.count_manager.get_max_counts(), institution_type=institution_type)
        # print(f"Made the context for the child as: \n{disease_context}")
        # print("\n")
        ## 1. Detect all diseases
        detected_diseases : list[DetectedDisease] = self.detector.detect()
        is_user_disease_selected = any(d.definition.name == child.diseaseName for d in detected_diseases)

        
        ## Start by first checking whether user disease is selected
        ## Because till now only the diseases through value changing is only been selected.
        logging.info(f"Is User given disease, which is : {child.diseaseName}. Is it seleted? {is_user_disease_selected}")

        # self.log_bp("Before selecting user given disease")

        if child.diseaseName.strip() and not is_user_disease_selected:
            ## Remember user has given us the concept, we need real valid disease too from the portal
            valid_variant = self.disease_variant_registry.get_correct_variant(disease_name=child.diseaseName,curr_age=get_age(child.dob))
            logging.info(f"for user disease: {child.diseaseName}, got variant as {valid_variant}")
            try:
                self._select_user_given_disease(disease_name=valid_variant,child=child,disease_context=disease_context)
            except:
                logging.error('Error happened while selecting user disease')

        # self.log_bp("After selecting user given disease")


        ## After doing user's disease thing check again
        detected_diseases : list[DetectedDisease] = self.detector.detect()
        logging.info(f"DiseaseManager: Got detected diseases for child: {child.name} as:\n{detected_diseases}")
        if detected_diseases:
            # print(f"Initial detected diseases are: \n{detected_diseases}")
            # print("====================================")
            # print("\n")
            for disease in detected_diseases:
                # self.log_bp(f"Before working with: {disease.definition.name}")
                logging.info(f"Now started for checking of disease : {disease.definition.name}")
                if disease.definition.name == child.diseaseName and disease.definition.name not in self.managed_disease_name:
                    logging.info("This disease is given by the user")
                    continue

                if disease.definition.name != child.diseaseName and disease.definition.name not in self.managed_disease_name:
                    ## This disease is wrongly selected by the portal
                    logging.info("This disease is wrongly selected by the portal so we are trying to remove it through checkbox.")
                    removal_strategy: DiseaseRemovalStrategy = CheckboxRemovalStrategy()

                    ## First check whether any removal strategy is present because disease like (microcephely, or macrocephely) are not managed disease. But they have there own removal strategies
                    logging.info("Let's first try removing this disease by finding the removal strategy")
                    if disease.definition.name in self.disease_removal_repo.get_all_disease_name_for_removal_strategy():

                        removal_strategy: DiseaseRemovalStrategy = self.disease_removal_repo.get_strategy_by_disease_name(disease_name=disease.definition.name)
                        logging.info(f"For disease {disease.definition.name} with removal strategy as {removal_strategy}")


                    is_disease_removed = removal_strategy.remove(disease=disease,page=self.page,synchronizer=self.synchronizer)
                    if not is_disease_removed:
                        raise Exception("Cannot remove this disease, so leaving")
                elif disease.definition.name in self.managed_disease_name:
                    logging.info("This is a managed disease. Now checking for validation")
                    ## Check rules
                    disease_rule = self.disease_rule_repo.get_rule(disease_name=disease.definition.name)
                    # print(f"Got rule for this disease as {disease_rule}")
                    if not disease_rule:
                        raise Exception("Cannot find disease rule for a managed disease")
                
                    if not disease_rule.validate(disease=disease, context=disease_context):
                        logging.info("This disease has not cleared validation test, so getting the removal strategy")
                        removal_strategy: DiseaseRemovalStrategy = self.disease_removal_repo.get_strategy_by_disease_name(disease.definition.name)
                        # logging.info(f"Got removal strategy as: {removal_strategy}")
                        # print(f"Got removal strategy as {removal_strategy}")
                        is_disease_removed = removal_strategy.remove(disease=disease,page=self.page,synchronizer=self.synchronizer)
                        if not is_disease_removed:
                            raise Exception("Cannot remove this disease, so leaving")
            
                # print("=========================================\n")
                # self.log_bp(f"After working with: {disease.definition.name} ")
        
        else:
            logging.info("Child is healthy")
                    
        
        ## TODO: Maybe we can assign a managed disease too here after deletion, if we can
        logging.info("Checking whether should we add any disease or not.")


        if child.diseaseName:
            logging.info(f"Child: {child.name} already has a disease given by the user as: {child.diseaseName}, so we are not adding any further diseases")
            ## Final output 
            final_diseases = self.detector.detect()
            print(f"Got final diseases as: {final_diseases}")
            for disease in final_diseases:
                if disease.definition.name in self.managed_disease_name:
                    ## Get the root concept of the disease
                    disease_concept = self.disease_variant_registry.get_disease_concept(disease_name=disease.definition.name)
                    ## Update the count
                    self.count_manager.increment(disease_concept)

        
            return final_diseases

        ## Let's check how many disease from addition repository satisfies rules for this child
        candidate_diseases = self.disease_addition_repo.get_all_disease_name_for_adding_strategy()
        # print(f"Candidate diseases are : {candidate_diseases}")
        for disease in candidate_diseases:
            # print("DiseaseManager:=====================================================\n")
            # print(f"Checking for candidate disease: {disease}")
            current_diseases = self.detector.detect()
            # print(f"Current diseases are as follows :\n{current_diseases}")

            if any(d.definition.name in candidate_diseases for d in current_diseases):
                logging.info(
                    "A disease from candidate list is already present. "
                    "Skipping disease addition."
                )
                break
            
            disease_rule = self.disease_rule_repo.get_rule(disease_name=disease)
            if not disease_rule:
                raise ValueError(f"Addition of disease : {disease} doesn't have rule")
            disease_def = self.full_diseases_repo.get_by_name(disease)

            # print(f"Got full disease as : \n{disease_def}\nGot full rule as : \n{disease_rule}")
            
            if disease_rule.validate(disease=DetectedDisease(definition=disease_def,source=DiseaseSource.UNKNOWN),context=disease_context):
                logging.info(f"This disease: {disease} got validated. Adding only this one.")
            #     ## Add the first disease that qualifies for simplicity
            #     ## Get adding strategy
                addition_strategy = self.disease_addition_repo.get_strategy_by_disease_name(disease_name=disease)
                if not addition_strategy:
                    logging.error("Can't found adding strategy for this one")
                    continue

                # print(f"Got addition strategy as : {addition_strategy}")
                is_disease_added = addition_strategy.add(child=child,page=self.page,synchronizer=self.synchronizer,repository=self.full_diseases_repo)
                if not is_disease_added:
                    logging.error(f"Cannot add this disease: {disease}. So trying next one.")
                    continue
                else:
                    logging.info(f"Added this disease succesfully: {disease}. Breaking out of the loop.")
                    break    
            else:
                logging.info(f"This disease {disease}.... failed validation rule test.")

            

            

        

        ## Final output 
        final_diseases = self.detector.detect()
        # print(f"Got final diseases as: {final_diseases}")
        for disease in final_diseases:
            if disease.definition.name in self.managed_disease_name:
                ## Get the root concept of the disease
                disease_concept = self.disease_variant_registry.get_disease_concept(disease_name=disease.definition.name)
                ## Update the count
                self.count_manager.increment(disease_concept)

        
        return final_diseases
        

