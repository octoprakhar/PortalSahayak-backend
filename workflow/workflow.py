import logging
from playwright.sync_api import Page
from typing import Callable

from services.loader import ChildLoader
from services.SamManager import SamManager
from workflow.ScreeningPage import ChildScreeningPage
from services.SearchStudent import SearchStudent
from all_models.SearchStudentModels import SearchResult
from workflow.ExistingChildrenWithoutData import ExistingChildrenWithoutData
from all_models.FeedbackResult import FeedbackResult,FeedbackOutcome
from all_models.ChildProcessingResult import ChildProcessingResult
from constants.log_type import LogType

from services.PageSynchronizer import PageSynchronizer
from disease.manager.DiseaseCountManager import DiseaseCountManager


class ScreeningWorkflow:
    def __init__(self, page:Page, logger:Callable[[str,LogType],None] = None, job_id: str = None, synchronizer: PageSynchronizer = None ):
        self.page = page
        self.loader = ChildLoader()
        self.job_id = job_id
        self.sam_manager = SamManager() ## Each workflow will get one sam manager
        self.logger = logger
        self.synchronizer = synchronizer
        self.count_manager = DiseaseCountManager()

    def run(self, excel_path, defaultContactNum: str, address: str = "") -> list[ChildProcessingResult]:
        logging.info("Data Loading started")
        children = self.loader.loadData(excel_path,defaultContactNum,address)
        failed_children = []

        for child in children:
            try:
                
                screening = ChildScreeningPage(page = self.page, child=child,job_id= self.job_id,sam_manager=self.sam_manager,synchronizer=self.synchronizer, count_manager=self.count_manager)
                ## TODO check whether child is sam or not. Workflow will manage total sam count, internally classes will ask sam and set weight and height accordingly

                searchStudent = SearchStudent(page=self.page, child=child)
                existingStudent: SearchResult | None = searchStudent.search()
                
                if existingStudent.found == True and existingStudent.eligible == True:
                    logging.info(f"🤩🤩 Child with name {child.name} already exists.")
                    existingStudentResult = screening.saveExistingChild(existingChildLocator=existingStudent.locator)

                    
                    if existingStudentResult.outcome is not FeedbackOutcome.SUCCESS:
                        failed_children.append(ChildProcessingResult(child_name=child.name,father_name=child.fatherName,outcome=existingStudentResult.outcome.value, message=existingStudentResult.message))
                else:
                    logging.info(f"🎉🎉 Child with {child.name} saved.")
                    newStudentResult = screening.submit()
                    if newStudentResult.outcome is not FeedbackOutcome.SUCCESS:
                        failed_children.append(ChildProcessingResult(child_name=child.name,father_name=child.fatherName,outcome=newStudentResult.outcome.value, message=newStudentResult.message))

                


            except Exception as e:
                logging.exception(
                    f"Failed to add child: {child.name}"
                )
                failed_children.append(ChildProcessingResult(child_name=child.name,father_name=child.fatherName, outcome=FeedbackOutcome.SYSTEM_ERROR.value,message="Internal error happened while saving"))
        
        ## Let's enter the existing child, that are not present in dataset given
        logging.info("📢📢📢📢📢📢📢📢📢📢 Starting with Existing children📢📢📢📢📢📢📢📢📢📢📢📢📢📢📢📢")
        try:
            existingChildrenWithoutData = ExistingChildrenWithoutData(mobileNumber=defaultContactNum, page=self.page, address=address,sam_manager=self.sam_manager, job_id=self.job_id,synchronizer=self.synchronizer, count_manager=self.count_manager)
            existingChildrenWithoutData.addExistingChildren()
        except Exception as e:
            logging.exception(f"Error while entering the existing students as: \n{e}")

        return failed_children