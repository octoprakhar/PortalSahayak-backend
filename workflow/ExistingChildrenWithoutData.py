## Children that are not given in data, but it is there in that institutions

from playwright.sync_api import Page
import logging
import re

from all_models.child_models import Child
from all_models.ExistingStudentModel import ExistingChildResult
from workflow.ScreeningPage import ChildScreeningPage
from services.CreateChild import ChildFactory
from utils.loaderUtils import get_age
from services.PageSynchronizer import PageSynchronizer
from disease.manager.DiseaseCountManager import DiseaseCountManager
from all_models.ChildRunResult import ChildRunResult
from all_models.ClassRange import ClassRange
from constants.WorkflowStage import WorkflowStage
from constants.ChildType import ChildType
from all_models.FeedbackResult import FeedbackOutcome

from constants.institution_type import InstitutionType

class ExistingChildrenWithoutData:
    def __init__(self, mobileNumber:str, page:Page,address:str, count_manager: DiseaseCountManager, selected_mapping: dict[str,str], max_children_count: int,institution_type: InstitutionType, existing_limit: int, class_range: ClassRange = None, job_id: str = None, synchronizer : PageSynchronizer = None):
        self.mobileNumber = mobileNumber
        self.page = page
        self.address = address
        self.job_id = job_id
        self.synchronizer = synchronizer
        self.count_manager = count_manager
        self.selected_mapping = selected_mapping
        self.institution_type = institution_type
        self.max_children_count = max_children_count
        self.class_range = class_range
        self.existing_limit = existing_limit

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
    
    def _get_class(self, class_str: str) -> int:
        """
        Convert a string like 'Class 9' (with optional leading/trailing spaces)
        into the integer 9.

        Returns 0 if the format is anything other than 'Class <number>'.
        """
        match = re.fullmatch(r"\s*Class\s+(\d+)\s*", class_str)
        if not match:
            return 0

        return int(match.group(1))

    def _filterByClass(self, class_no: int):
        """
        Select a class from dropdown and click Search.
        """

        logging.info(f"Filtering for Class {class_no}")

        self.page.locator("#screeningClassFilter").select_option(str(class_no))

        self.page.get_by_role(
            "button",
            name="Search",
            exact=True
        ).click()


    def _getAllChild(self) -> list[ExistingChildResult]:
        """
        Returning all the children currently showing on the table without clicking the next button, 
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
            child_class = None

            if self.institution_type == InstitutionType.SCHOOL:
                child_class_str = get_cell("Class")
                child_class = self._get_class(class_str=child_class_str)



            all_children.append(ExistingChildResult(name=name, dob=dob, fatherName=fatherName, motherName=motherName, gender=gender, isStartScreeningButtonPresent=isStartScreeningButtonPresent, child_class=child_class ))


        return all_children
    
    def _eligibleChildren(
        self, existingChildrenList: list[ExistingChildResult]
    ) -> list[ExistingChildResult]:
        """
        Returns all eligible children.

        - AWC:
            - Age < 6
            - Start Screening button present
        - SCHOOL:
            - Age < 19
            - Start Screening button present
            - Child's class lies within the configured class range (inclusive)
        """
        eligibleChildren = []

        for child in existingChildrenList:
            age = get_age(child.dob)

            # logging.info(
            #     f"Checking eligibility of {child.name} "
            #     f"with age {age}, "
            #     f"start screening={child.isStartScreeningButtonPresent}, "
            #     f"class={child.child_class}"
            # )

            if not child.isStartScreeningButtonPresent:
                continue

            if self.institution_type == InstitutionType.AWC:
                if age < 6:
                    eligibleChildren.append(child)

            elif self.institution_type == InstitutionType.SCHOOL:
                logging.info(f"Got school child. And child details are like this {child.child_class} and it's type is {type(child.child_class)}")
                if age >= 19:
                    continue

                if (
                    self.class_range is not None
                    and child.child_class is not None
                    and self.class_range.from_class
                    <= child.child_class
                    <= self.class_range.to_class
                ):
                    eligibleChildren.append(child)

        return eligibleChildren
    
    def addExistingChildren(self)->list[ChildRunResult]:

        ## Step 0 : Get number of pages, in pagination, that times I need to loop and click 'next' button
        all_child_results = []

        logging.info(f"In initial of existing child without data, current class range is {self.class_range}")

        if (
            self.institution_type == InstitutionType.SCHOOL
            and self.class_range is not None
        ):
            logging.info(f"Institution type is school and class range in not none")
            class_list = range(
                self.class_range.from_class,
                self.class_range.to_class + 1
            )
        else:
            class_list = [None]

        curr_count = 0
        
        for current_class in class_list:
            logging.info(f"Got current class as: {current_class}, and type is {type(current_class)}")
            if current_class is not None:
                logging.info(f"Current class is not none it is : {current_class}, and type is {type(current_class)}")
                self._filterByClass(class_no=current_class)
            else:
                logging.info("Current class is none")

            pages = self._getNumberOfPages()
            logging.info(f"Got number of pages as {pages}")
            logging.info(f"Got existing limit as : {self.existing_limit}")
            if self.class_range:
                logging.info(f"Got class range from class : {self.class_range.from_class} to {self.class_range.to_class}")
            else:
                logging.info(f"No class range is given")
                    
            for curr_page in range(1, pages + 1):
            
                if curr_count >= self.existing_limit:
                    break
            
                logging.info(f"Moving to page {curr_page}")
            
                self._goToPage(curr_page)
            
                all_children = self._getAllChild()
            
                eligible_children = self._eligibleChildren(all_children)
            
                logging.info(
                    "Eligible children:\n%s",
                    "\n".join(
                        f"  - Name: {c.name}, Age: {get_age(c.dob)}, Class: {c.child_class}, "
                        f"DOB: {c.dob}, Gender: {c.gender}"
                        for c in eligible_children
                    ) or "  None"
                )
            
                for child in eligible_children:
                    if curr_count >= self.existing_limit:
                        break
            
                    try:
            
                        childFactory = ChildFactory(
                            child=child,
                            defaultContactNumber=self.mobileNumber,
                            address=self.address
                        )
            
                        created_child = childFactory.createChild()
                        child_result = ChildRunResult(child=created_child,stage=WorkflowStage.PERSONAL_DETAILS, child_type=ChildType.EXISTING_CHILD_WITHOUT_DATA)
            
                        child_screening = ChildScreeningPage(
                            page=self.page,
                            child=created_child,
                            job_id=self.job_id,
                            synchronizer=self.synchronizer,
                            count_manager=self.count_manager,
                            selected_mapping=self.selected_mapping,
                            institution_type=self.institution_type
                                    
                        )
                        child_result.stage = WorkflowStage.HEALTH_DETAILS
                        # NO locator needed now
                        final_child_result = child_screening.saveExistingChild(existing_child_result=child_result)
                        if final_child_result.feedback.outcome == FeedbackOutcome.SUCCESS:
                            curr_count += 1
            
                        all_child_results.append(final_child_result)
            
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
            
        return all_child_results