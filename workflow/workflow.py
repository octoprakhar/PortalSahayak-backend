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

from services.PageSynchronizer import PageSynchronizer
from disease.manager.DiseaseCountManager import DiseaseCountManager
from services.ReportCreator import ReportCreator


class ScreeningWorkflow:
    def __init__(self, page:Page,report_creator: ReportCreator,  logger:Callable[[str,LogType],None] = None, job_id: str = None, synchronizer: PageSynchronizer = None ):
        self.page = page
        self.loader = ChildLoader()
        self.job_id = job_id
        self.report_creator = report_creator
        self.logger = logger
        self.synchronizer = synchronizer
        self.count_manager = DiseaseCountManager()

    def run(self, excel_path, defaultContactNum: str, address: str = ""):
        logging.info("Data Loading started")
        children = self.loader.loadData(excel_path,defaultContactNum,address)


        for child in children:
            try:
                
                screening = ChildScreeningPage(page = self.page, child=child,job_id= self.job_id,synchronizer=self.synchronizer, count_manager=self.count_manager)
                ## TODO check whether child is sam or not. Workflow will manage total sam count, internally classes will ask sam and set weight and height accordingly

                searchStudent = SearchStudent(page=self.page, child=child)
                existingStudent: SearchResult | None = searchStudent.search()
                
                if existingStudent.found == True and existingStudent.eligible == True:
                    logging.info(f"🤩🤩 Child with name {child.name} already exists.")
                    existingStudentResult = screening.saveExistingChild(existingChildLocator=existingStudent.locator)

                    
                    if existingStudentResult.feedback.outcome is not FeedbackOutcome.SUCCESS:
                        self.report_creator.add_failure(existingStudentResult)
                    else:
                        self.report_creator.add_success(existingStudentResult)
                else:
                    logging.info(f"🎉🎉 Child with {child.name} saved.")
                    newStudentResult = screening.submit()
                    if newStudentResult.feedback.outcome is not FeedbackOutcome.SUCCESS:
                        self.report_creator.add_failure(newStudentResult)
                    else:
                        self.report_creator.add_success(newStudentResult)

                


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
        try:
            existingChildrenWithoutData = ExistingChildrenWithoutData(mobileNumber=defaultContactNum, page=self.page, address=address, job_id=self.job_id,synchronizer=self.synchronizer, count_manager=self.count_manager)
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
