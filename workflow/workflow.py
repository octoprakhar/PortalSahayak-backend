import logging
from playwright.sync_api import Page

from services.loader import ChildLoader
from workflow.ScreeningPage import ChildScreeningPage
from services.SearchStudent import SearchStudent
from all_models.SearchStudentModels import SearchResult
from workflow.ExistingChildrenWithoutData import ExistingChildrenWithoutData

class ScreeningWorkflow:
    def __init__(self, page:Page):
        self.page = page
        self.loader = ChildLoader()

    def run(self, excel_path, defaultContactNum: str, address: str = ""):
        logging.info("Data Loading started")
        children = self.loader.loadData(excel_path,defaultContactNum,address)

        for child in children:
            try:
                screening = ChildScreeningPage(self.page, child)
                searchStudent = SearchStudent(page=self.page, child=child)
                existingStudent: SearchResult | None = searchStudent.search()
                
                if existingStudent.found == True and existingStudent.eligible == True:
                    logging.info(f"🤩🤩 Child with name {child.name} already exists.")
                    screening.saveExistingChild(existingChildLocator=existingStudent.locator)
                else:
                    logging.info(f"🎉🎉 Child with {child.name} saved.")
                    screening.submit()

                


            except Exception as e:
                logging.exception(
                    f"Failed to add child: {child.name}"
                )
        
        ## Let's enter the existing child, that are not present in dataset given
        logging.info("📢📢📢📢📢📢📢📢📢📢 Starting with Existing children📢📢📢📢📢📢📢📢📢📢📢📢📢📢📢📢")
        existingChildrenWithoutData = ExistingChildrenWithoutData(mobileNumber=defaultContactNum, page=self.page, address=address)
        existingChildrenWithoutData.addExistingChildren()