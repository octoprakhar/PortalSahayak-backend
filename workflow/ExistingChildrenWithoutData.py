## Children that are not given in data, but it is there in that institutions

from playwright.sync_api import Page
import logging
import re

from all_models.child_models import Child
from all_models.ExistingStudentModel import ExistingChildResult
from workflow.ScreeningPage import ChildScreeningPage
from services.CreateChild import ChildFactory
from utils.loaderUtils import get_age


class ExistingChildrenWithoutData:
    def __init__(self, mobileNumber:str, page:Page,address:str):
        self.mobileNumber = mobileNumber
        self.page = page
        self.address = address

    def _getNumberOfPages(self) -> int | None:
        page_info = self.page.locator(
            r'div:text-matches("^Page\\s+\\d+\\s+of\\s+\\d+$")'
        )

        text = page_info.text_content()

        if not text:
            return None

        match = re.search(r'of\s+(\d+)', text)

        if not match:
            return None

        return int(match.group(1))
    
    def _resetToFirstPage(self):

        while True:

            previous_btn = self.page.get_by_role(
                "button",
                name="Prev",
                exact=True
            )

            if not previous_btn.is_enabled():
                break

            previous_btn.click()

            self.page.wait_for_timeout(1000)
    
    def _goToPage(self, target_page: int):

        # first return to page 1
        self._resetToFirstPage()

        # already reached
        if target_page == 1:
            return

        # move forward
        for _ in range(target_page - 1):

            next_btn = self.page.locator(
                "button",
                has_text="Next"
            )

            next_btn.wait_for(state="visible")

            if not next_btn.is_enabled():

                raise Exception(
                    f"Cannot move to page {target_page}"
                )

            next_btn.click()

            self.page.wait_for_timeout(1000)
    
    def _normalizeDob(self,dob:str):
        """
        Changes age from yyyy-mm-dd to dd-mm-yyyy
        """
        dob_parts = dob.strip().split("-")[::-1]
        return "-".join(dob_parts)


    def _getAllChild(self) -> list[ExistingChildResult]:
        """
        Returning all the children currently showing on the table, without clicking the next button,
        using column names instead of hardcoded indexes so it survives
        column reordering/addition/removal
        """
        all_children = []

        headers = self.page.locator("table thead th")

        column_map = {
            headers.nth(i).inner_text().strip(): i
            for i in range(headers.count())
        }
        rows = self.page.locator("table tbody tr")
        rowCount = rows.count()

        for i in range(rowCount):
            row = rows.nth(i)
            cells = row.locator("td")

            def get_cell(header_name: str) -> str:
                index = column_map[header_name]
                return cells.nth(index=index).inner_text().strip()
            
            name = get_cell("Name")
            gender = get_cell("Gender")
            dob = self._normalizeDob(get_cell("DOB"))
            fatherName = get_cell("Father's Name")
            motherName = get_cell("Mother's Name")

            # Infer screening state from Health Status column
            # Screened rows have values like "Healthy"
            # Unscreened rows are empty
            health_status = get_cell("Health Status")

            isStartScreeningButtonPresent = not bool(health_status)


            all_children.append(ExistingChildResult(name=name, dob=dob, fatherName=fatherName, motherName=motherName, gender=gender, isStartScreeningButtonPresent=isStartScreeningButtonPresent ))


        return all_children
    
    def _eligibleChildren(self, existingChildrenList: list[ExistingChildResult]) -> list[ExistingChildResult]:
        """
        All child who are below 5 years of age, and has startScreening button present should get return, and they must be on that page, without next 
        button to change the pagination
        """
        eligibleChildren = []

        for child in existingChildrenList:
            logging.info(f"Checking eligibility of {child.name} with age {get_age(child.dob)}, and start screeining as {child.isStartScreeningButtonPresent}")
            age = get_age(child.dob)
            if age < 6 and child.isStartScreeningButtonPresent:
                eligibleChildren.append(child)

        
        return eligibleChildren

    
    def addExistingChildren(self)->None:

        ## Step 0 : Get number of pages, in pagination, that times I need to loop and click 'next' button
        pages = self._getNumberOfPages()
        logging.info(f"Got number of pages as {pages}")
        nextBtn = self.page.locator("button",has_text="Next")
        for curr_page in range(1, pages + 1):

            logging.info(f"Moving to page {curr_page}")

            self._goToPage(curr_page)

            all_children = self._getAllChild()

            eligible_children = self._eligibleChildren(all_children)

            for child in eligible_children:

                try:

                    childFactory = ChildFactory(
                        child=child,
                        defaultContactNumber=self.mobileNumber,
                        address=self.address
                    )

                    created_child = childFactory.createChild()

                    child_screening = ChildScreeningPage(
                        self.page,
                        created_child
                    )

                    # NO locator needed now
                    child_screening.saveExistingChild()

                    logging.info(
                        f"Saved child {child.name}"
                    )

                    # IMPORTANT
                    # website reset to page 1 after save
                    # so return back to current page
                    self._goToPage(curr_page)

                except Exception as e:

                    logging.exception(
                        f"Error saving child {child.name}: {e}"
                    )