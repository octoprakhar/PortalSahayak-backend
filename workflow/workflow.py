import logging
from playwright.sync_api import Page
from typing import Callable

from services.loader import ChildLoader
from workflow.ScreeningPage import ChildScreeningPage
from services.SearchStudent import SearchStudent
from all_models.SearchStudentModels import SearchResult
from workflow.ExistingChildrenWithoutData import ExistingChildrenWithoutData
from all_models.FeedbackResult import FeedbackResult,FeedbackOutcome
from all_models.ChildProcessingResult import ChildProcessingResult
from constants.log_type import LogType
from constants.ChildType import ChildType
from all_models.ChildRunResult import ChildRunResult
from all_models.ClassRange import ClassRange

from services.PageSynchronizer import PageSynchronizer
from services.ReportCreator import ReportCreator
from disease.factory.DiseaseCountFactory import DiseaseCountFactory
from services.ExistingChildScanner import ExistingChildScanner


class ScreeningWorkflow:
    def __init__(self, page:Page,report_creator: ReportCreator, selected_mapping: dict[str,str], institution_type: str, existing_limit: int, logger:Callable[[str,LogType],None] = None, job_id: str = None, synchronizer: PageSynchronizer = None, class_range : ClassRange = None ):
        self.page = page
        self.loader = ChildLoader()
        self.job_id = job_id
        self.report_creator = report_creator
        self.logger = logger
        self.synchronizer = synchronizer
        self.selected_mapping = selected_mapping
        self.institution_type = institution_type
        self.class_range = class_range
        self.existing_limit = existing_limit


    def run(self, excel_path, defaultContactNum: str, address: str = ""):
        logging.info("Data Loading started")
        children = self.loader.loadData(excel_path,defaultContactNum,address)

        new_child_disease_manager = DiseaseCountFactory().create(max_len=len(children))

        logging.info(f"Got new disease manager max as : {new_child_disease_manager.get_max_counts()}")


        for child in children:
            try:
                
                screening = ChildScreeningPage(page = self.page, child=child,job_id= self.job_id,synchronizer=self.synchronizer, count_manager=new_child_disease_manager,selected_mapping=self.selected_mapping, institution_type=self.institution_type)
                ## TODO check whether child is sam or not. Workflow will manage total sam count, internally classes will ask sam and set weight and height accordingly

                searchStudent = SearchStudent(page=self.page, child=child, institution_type=self.institution_type)
                existingStudent: SearchResult | None = searchStudent.search()

                logging.info(f"For child: {child.name}. Search result is {existingStudent}")
                
                if existingStudent.found == True and existingStudent.eligible == True:
                    logging.info(f"🤩🤩 Child with name {child.name} already exists.")
                    existingStudentResult = screening.saveExistingChild(existingChildLocator=existingStudent.locator)

                    
                    if existingStudentResult.feedback.outcome is not FeedbackOutcome.SUCCESS:
                        self.report_creator.add_failure(existingStudentResult)
                    else:
                        self.report_creator.add_success(existingStudentResult)
                elif existingStudent.found == False:
                    logging.info(f"🎉🎉 Child with {child.name} saved.")
                    newStudentResult = screening.submit()
                    if newStudentResult.feedback.outcome is not FeedbackOutcome.SUCCESS:
                        self.report_creator.add_failure(newStudentResult)
                    else:
                        self.report_creator.add_success(newStudentResult)
                else:
                    ## We are making duplicate copy
                    self.report_creator.add_failure(ChildRunResult(child=child,child_type=ChildType.EXISTING_CHILD,feedback=FeedbackResult(outcome=FeedbackOutcome.DUPLICATE,message="This child is already present")))
                    logging.info(f"Child : {child.name} is already screened. So just moving forward")
                    SearchStudent.clear_search_text(page=self.page)
                    continue

                


            except Exception as e:
                logging.exception(
                    f"Failed to add child: {child.name}"
                )
                result = ChildRunResult(
                    child=child,
                    feedback=FeedbackResult(
                        outcome=FeedbackOutcome.SYSTEM_ERROR,
                        message=str(e)
                    )
                )

                self.report_creator.add_failure(result)

                continue
        
        ## Let's enter the existing child, that are not present in dataset given
        logging.info("📢📢📢📢📢📢📢📢📢📢 Starting with Existing children📢📢📢📢📢📢📢📢📢📢📢📢📢📢📢📢")
        scanner = ExistingChildScanner(page=self.page, is_awc_screening= self.institution_type == "awc", class_range= self.class_range if self.institution_type == "school" else None)
        total_existing = scanner.get_total_existing_student()

        existing_limit = min(
            total_existing,
            self.existing_limit  ## Just checking I will change it later
        )
        existing_children_count_manager = DiseaseCountFactory().create(max_len=existing_limit)
        logging.info(f"Got existing disease manager max as : {existing_children_count_manager.get_max_counts()}")
        try:
            existingChildrenWithoutData = ExistingChildrenWithoutData(mobileNumber=defaultContactNum, page=self.page, address=address, job_id=self.job_id,synchronizer=self.synchronizer, count_manager=existing_children_count_manager,selected_mapping=self.selected_mapping, institution_type=self.institution_type, max_children_count=existing_limit, class_range=self.class_range, existing_limit=existing_limit)
            non_data_existing_children_results = existingChildrenWithoutData.addExistingChildren()
            for child_result in non_data_existing_children_results:
                if child_result.feedback.outcome is not FeedbackOutcome.SUCCESS:
                    self.report_creator.add_failure(child_result=child_result)
                else:
                    self.report_creator.add_success(child_result=child_result)
        except Exception as e:
            logging.exception(f"Error while entering the existing students as: \n{e}")
            self.logger(
                "Failed while processing existing children without data",
                LogType.ERROR
            )
