# To use this class after creating browser instant, and entering in the "Adding" page
# This class is simply saying "give me the page object, and the child and I will save it"
import logging
from playwright.sync_api import Page,Locator

from typing import Callable

from all_models.child_models import Child
from services.PortalFeedbackDetector import PortalFeedbackDetector
from services.SearchStudent import SearchStudent
from all_models.FeedbackResult import FeedbackResult,FeedbackOutcome
from all_models.ChildRunResult import ChildRunResult
from constants.WorkflowStage import WorkflowStage
from constants.log_type import LogType
from constants.ChildType import ChildType
from constants.institution_type import InstitutionType
from all_models.JobLogs import JobLog
from utils.loaderUtils import get_age,get_corrected_values
from services.PageSynchronizer import PageSynchronizer


from disease.manager.DiseaseManager import DiseaseManager
from disease.manager.DiseaseCountManager import DiseaseCountManager
from disease.models.DiseaseDefinition import DiseaseDefinition
from disease.models.DetectedDisease import DetectedDisease

from facility.manager.FacilityManager import FacilityManager
from facility.rule.FacilityMappingRule import FacilityMappingRule


class ChildScreeningPage:
    def __init__(self, page:Page, child:Child, count_manager: DiseaseCountManager,selected_mapping: dict[str,str], institution_type: str, logger: Callable[[str,LogType],None] = None, job_id: str = None, synchronizer: PageSynchronizer = None):
        self.page = page
        self.child = child
        self.job_id = job_id
        self.count_manager = count_manager
        self.logger = logger
        self.age = get_age(self.child.dob)
        self.synchronizer = synchronizer
        self.selected_mapping = selected_mapping
        self.institution_type = institution_type

    
    def _fill_if_visible(self,selector, value):
        field = self.page.locator(selector)
        if field.count() > 0 and field.is_visible():
            field.fill(str(value))

    def _select_if_visible(self,selector, value):
        field = self.page.locator(selector)
        if field.count() > 0 and field.is_visible():
            field.select_option(label=str(value))

    def _fill_bp_if_visible(self):
        field = self.page.locator('[name="bloodPressureValue"]')
        if field.count() > 0 and field.is_visible():
            field.fill(str(self.child.bloodPressure))
            field.press("Tab")  # Move focus away to trigger blur/change
            self.synchronizer.wait_for_setting_blood_pressure(page=self.page)

    def _skip_child(self):
        """
        For a reason if we don't have to enter this child just go to
        main screening page
        """
        ## When DUPLICATE IS PRESENT
        duplicate_record = self.page.locator(
            'h3:text-is("Duplicate Record Found")'
        )

        if duplicate_record.is_visible():
            try:
                close_btn = self.page.get_by_role("button", name="Close")
                close_btn.wait_for(state="visible", timeout=5000)
                close_btn.click()
            except TimeoutError:
                pass
        
        ## When child health data is saving
        child_register = self.page.get_by_role("heading", name="👨‍👩‍👧‍👦 Personal & Family Details")

        if child_register.is_visible():
            logging.info("We are in page for entering child registration, now returning")
            try:
                cancel_btn = self.page.get_by_role("button", name="Cancel")
                cancel_btn.wait_for(state="visible", timeout=5000)
                cancel_btn.click()
            except TimeoutError:
                pass

        health_register = self.page.get_by_role("heading", name="Screening for Health Conditions")

        if health_register.is_visible():
            try:
                back_btn = self.page.get_by_role("button", name="Back")
                back_btn.wait_for(state="visible", timeout=5000)
                back_btn.click()
            except TimeoutError:
                pass

        ## For last preview screen
        prev_heading = self.page.get_by_role("heading", name="Screening Preview")
        if prev_heading.is_visible():
            try:
                self.page.get_by_role("button", name="Back to Edit").click()
                back_btn = self.page.get_by_role("button", name="Back")
                back_btn.wait_for(state="visible", timeout=5000)
                back_btn.click()

            except Exception:
                pass




        ## And also clear the search bar if exists
        SearchStudent.clear_search_text(self.page)

    def _log_job(self, log_type: LogType, message: str):
        logging.info(f"Job log is called for child : {self.child.name}, with job_id: {self.job_id}")
        if not self.job_id:
            logging.info("Can't find job ID")
            return

        if self.logger:
            self.logger(message,log_type)
            return
        
    def _log_child(self, log_type: LogType, message: str):
        self._log_job(
            log_type,
            f"{self.child.name}, C/o- {self.child.fatherName}: {message}"
        )

    def _log_feedback(self, feedback: FeedbackResult):
        logging.info(f"Log feedback is called for child: {self.child.name}, with feeback as : {feedback}")
        self._log_child(
            LogType.INFO,
            "Processing started"
        )
        if feedback.outcome == FeedbackOutcome.DUPLICATE:
            self._log_child(
                LogType.ERROR,
                "Duplicate entry found."
            )
            return

        if feedback.outcome == FeedbackOutcome.VALIDATION_ERROR:
            self._log_child(
                LogType.ERROR,
                ",".join(feedback.validation_errors)
            )
            return

        if feedback.outcome == FeedbackOutcome.FAILURE or feedback.outcome == FeedbackOutcome.UNKNOWN:
            self._log_child(
                LogType.ERROR,
                feedback.message
            )
            return

        if feedback.outcome == FeedbackOutcome.SUCCESS:
            self._log_child(
                LogType.SUCCESS,
                feedback.message
            )

    def _fill_final_health_values(self, result: ChildRunResult):
        height = self.page.locator('[name="height"]')
        weight = self.page.locator('[name="weight"]')
        hb = self.page.locator('[name="hb"]')
        head_circum = self.page.locator('[name="headCircumference"]')

        result.final_height = height.input_value() if height.count() > 0 else None
        result.final_weight = weight.input_value() if weight.count() > 0 else None
        result.final_hb = hb.input_value() if hb.count() > 0 else None
        result.final_head_circumference = (
            head_circum.input_value() if head_circum.count() > 0 else None
        )



    def insertPersonalDetails(self) -> FeedbackResult:
        ## We will take it from loaded excel his name, father's name, mother's name, DOB, address, mobile number
        ## Then perform this 

        button_name = (
            "Add New Child"
            if self.institution_type == InstitutionType.AWC.value
            else "Add New Student"
        )
        # print(f"Got institution Type as {institution_data.institution_type}")
        buttons = self.page.get_by_role("button", name=button_name)
        buttons.first.click()

        ## IF target complete box appears 
        message = self.page.get_by_text(
            "Planned children for this institution have been screened. Do you want to screen more?",
            exact=True
        )

        if message.is_visible():
            self.page.get_by_role("button", name="Yes, proceed!").click()        

        self.page.wait_for_timeout(1000)
        self.page.get_by_role('button',name="Proceed").click()
        childNameField = self.page.locator('[name="studentName"]')
        dobField = self.page.locator('[placeholder="dd-mm-yyyy"]')
        genderDropDown = self.page.locator('[name="gender"]')
        motherNameField = self.page.locator('[name="motherName"]')
        fatherNameField = self.page.locator('[name="fatherName"]')
        mobileNumberField = self.page.locator('[name="mobile"]')
        addressField = self.page.locator('[name="address"]')
        ageField = self.page.locator('[name="age"]')
    


        childNameField.fill(self.child.name)
        dobField.fill(self.child.dob)
        # random_number = random.randint(0, 9)
        genderDropDown.select_option(label=self.child.gender)
        ## For testing
        # if random_number >= 5:
            
        motherNameField.fill(self.child.motherName)
        fatherNameField.fill(self.child.fatherName)
        mobileNumberField.fill(self.child.mobileNumber)
        addressField.fill(self.child.address)

        ## Selecting class if visible
        # logging.info(f"Got child class as {self.child.childClass} and type is {type(self.child.childClass)}")
        self._select_if_visible('select[name="className"]',f'Class {self.child.childClass}')

        ## Saving age as global variable

        if float(ageField.input_value()) < 1:
            birthWeightField = self.page.locator('[name="birthWeight"]')
            birthWeightField.fill("2500")
    

        logging.info("Please press enter to move forward....")

        saveChildBtn = self.page.get_by_role('button',name='Save & Start Screening')
        saveChildBtn.click()

        # Waiting and detecting if success and failure by UI
        self.synchronizer.wait_loading(page=self.page)
        current_page_locator = self.page.get_by_role("heading", name="👨‍👩‍👧‍👦 Personal & Family Details")
        next_page_locator = self.page.get_by_role("heading", name="Screening for Health Conditions")
        next_page_locator.wait_for(state="visible",timeout=1500)
        portalFeedback = PortalFeedbackDetector(self.page,success_msg="Successfully inserted child detail")
        print(f"Is next page visible for new child entry as after loading: {next_page_locator.is_visible()}")

        feedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
        return feedbackResult


    def insertHealthReport(self,result: ChildRunResult) -> FeedbackResult:

        heightField = self.page.locator('[name="height"]')
        weightField = self.page.locator('[name="weight"]')
        hbField = self.page.locator('[name="hb"]')
        

        # random_number = random.randint(0, 9)
        # if random_number >= 5:
        heightField.fill(self.child.height)
        
        weightField.fill(self.child.weight)

        hbField.fill(self.child.hb)
        

        try:
            self.page.wait_for_function("""
                () => {
                    const w = document.querySelector(
                        'select[name="weightAgeClassification"]'
                    )?.value;

                    const l = document.querySelector(
                        'select[name="lengthAgeClassification"]'
                    )?.value;

                    const wh = document.querySelector(
                        'select[name="weightHeightClassification"]'
                    )?.value;

                    return w !== "0" &&
                        l !== "0" &&
                        wh !== "0";
                }
                """, timeout=5000)
        except Exception as e:
            logging.error(f"Error occured while trying to get functions correct: {e}")
            return FeedbackResult(outcome=FeedbackOutcome.FAILURE, message=e.message)
        

        self._fill_if_visible('[name="headCircumference"]', self.child.headCircumference)
        self._fill_if_visible('[name="muac"]', "13")
        # logging.info("filling bp")
        # self._fill_bp_if_visible()
        # logging.info("selected bp")
        # self.page.wait_for_timeout(5000)

        self._select_if_visible('select[name="visionLeft"]', self.child.visionLeft)
        self._select_if_visible('select[name="visionRight"]', self.child.visionRight)

        # self.page.wait_for_timeout(5000)

        ## Calling disease manager for final check
        disease_manager = DiseaseManager(page=self.page, synchronizer=self.synchronizer, count_manager=self.count_manager)
        final_detected_diseases = disease_manager.manage(child=self.child)
        # print(f"Got classfication of bp after final disease from disease manager is filled as : {bp_classification.input_value()}")

        ## Now filling the derived values like BP
        self._fill_bp_if_visible()

        ## Call facility manager
        facility_mapping_rule = FacilityMappingRule()
        facility_manager = FacilityManager(page=self.page,mapping_rules=facility_mapping_rule,selected_mapping=self.selected_mapping,synchronizer=self.synchronizer)
        facility_manager.manage(detected_diseases=final_detected_diseases)

        ## Fill latest values
        self._fill_final_health_values(result=result)
        result.final_diseases = [d.definition.name for d in final_detected_diseases]

        finalSubmitBtn = self.page.get_by_role('button',name='Preview & Submit')
        # self.page.wait_for_timeout(5000)
        finalSubmitBtn.click()
        self.synchronizer.wait_loading(page=self.page)
        
        portalFeedback = PortalFeedbackDetector(self.page, success_msg="Succesfully saved child health detail, moving to final submission.")
        current_page_locator = self.page.get_by_role("heading", name="Screening for Health Conditions")
        next_page_locator = self.page.get_by_role("heading", name="Screening Preview")
        feedbackResult: FeedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
        return feedbackResult



    def saveExistingChild(self, existingChildLocator: Locator = None, existing_child_result : ChildRunResult = None) -> ChildRunResult:
        """
        Saves the existing child.
        If no locator is provided, locate the row using self.child details.
        """
        child_result = ChildRunResult(child=self.child,child_type=ChildType.EXISTING_CHILD,stage=WorkflowStage.PERSONAL_DETAILS)



        if existingChildLocator is None:

            # Build header -> column index map
            headers = self.page.locator("table thead th")

            column_map = {
                headers.nth(i).inner_text().strip(): i
                for i in range(headers.count())
            }

            rows = self.page.locator("table tbody tr")

            target_name = self.child.name.strip().lower()
            target_father = self.child.fatherName.strip().lower()

            editChildButton = None

            for i in range(rows.count()):

                row = rows.nth(i)
                cells = row.locator("td")

                def get_cell(header_name: str) -> str:
                    return (
                        cells
                        .nth(column_map[header_name])
                        .inner_text()
                        .strip()
                        .lower()
                    )

                name = get_cell("Name")
                father_name = get_cell("Father's Name")

                if (
                    name == target_name
                    and father_name == target_father
                ):

                    logging.info(
                        f"Matched child row: {name} / {father_name}"
                    )

                    actions_cell = cells.nth(
                        column_map["Screening Actions"]
                    )

                    editChildButton = actions_cell.locator(
                        'div[title="Start Screening"]'
                    )

                    break

            if editChildButton is None:
                raise Exception(
                    f"Could not find child {self.child.name}"
                )

        else:

            # Existing locator should already be the row
            headers = self.page.locator("table thead th")

            column_map = {
                headers.nth(i).inner_text().strip(): i
                for i in range(headers.count())
            }

            actions_cell = (
                existingChildLocator
                .locator("td")
                .nth(column_map["Screening Actions"])
            )

            editChildButton = actions_cell.locator(
                'div[title="Start Screening"]'
            )

        editChildButton.click()

        
        if self.job_id:

            if self.logger:
                self.logger(f"{self.child.name} C/o- {self.child.fatherName} : is already exist.",LogType.INFO)


        ## Check if target of students are completed then just press 'Yes proceed button automatically'
        
        message = self.page.get_by_text(
            "Planned children for this institution have been screened. Do you want to screen more?",
            exact=True
        )

        if message.is_visible():
            self.page.get_by_role("button", name="Yes, proceed!").click()
            

        self.synchronizer.wait_loading(page=self.page)

        healthReportFeedbackResult = self.insertHealthReport(result=child_result if existing_child_result is None else existing_child_result)
        self._log_feedback(healthReportFeedbackResult)
        if healthReportFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
            self._skip_child()
            if existing_child_result is None:
                child_result.feedback = healthReportFeedbackResult
            else:
                existing_child_result.feedback = healthReportFeedbackResult

            return child_result if existing_child_result is None else existing_child_result
        # self.page.wait_for_timeout(1500)

        if existing_child_result:
            existing_child_result.stage = WorkflowStage.FINAL_SUBMIT
        else:
            child_result.stage = WorkflowStage.FINAL_SUBMIT

        mobileNumberField = self.page.locator(
        'input[placeholder="Enter Mobile"]'
        )

        if mobileNumberField.is_visible(timeout=1500):
            mobileNumberField.fill(
                self.child.mobileNumber
            )
        else:
            logging.info(
            "Mobile field absent. Skipping."
            )

        confirmClickBtn = self.page.get_by_role(
            "button",
            name="Confirm & Submit"
        )

        confirmClickBtn.click()

        self.synchronizer.wait_loading(page=self.page)
        # self.page.wait_for_timeout(1500)
        portalFeedback = PortalFeedbackDetector(self.page, success_msg="Sucessfully saved existing child's detail")
        current_page_locator = self.page.get_by_role("heading", name="Screening Preview")
        next_page_locator = self.page.get_by_role("button", name="+ Add New Child")
        next_page_locator.wait_for(state="visible",timeout=1500)
        finalFeedbackResult: FeedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
        self._log_feedback(finalFeedbackResult)
        if finalFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
            self._skip_child()
            if existing_child_result is None:
                child_result.feedback = finalFeedbackResult
            else:
                existing_child_result.feedback = finalFeedbackResult

            return child_result if existing_child_result is None else existing_child_result
        
        if existing_child_result is None:
            child_result.feedback = finalFeedbackResult
        else:
            existing_child_result.feedback = finalFeedbackResult

        return child_result if existing_child_result is None else existing_child_result


        


    

    def submit(self) -> ChildRunResult:

        ## If child is above 6years and It is awc don't enter here
        childRunResult = ChildRunResult(child=self.child,stage=WorkflowStage.PERSONAL_DETAILS,child_type=ChildType.NEW_CHILD)
        if self.age > 6 and self.institution_type == InstitutionType.AWC.value:
            logging.info(f"📢📢 Got child of name: {self.child.name} has age greater than 6 and we are doing AWC so leaving.")
            feedback = FeedbackResult(outcome=FeedbackOutcome.INVALID_DATA, message=f"Got child of name: {self.child.name} has age greater than 6 and we are doing AWC so leaving.")
            childRunResult.feedback = feedback
            return childRunResult
        ## Add child's personal detail and then add it's health report of each child, and then go


        ## For each child
        try:
            logging.info("🎁🎁🎁Started the process of initial saving of child detail.")
            registerFeedbackResult = self.insertPersonalDetails()
            self._log_feedback(registerFeedbackResult)
            if registerFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
                self._skip_child()
                childRunResult.feedback = registerFeedbackResult
                return childRunResult
            
            logging.info("🎁🎁🎁Started the process of health report saving of child detail.")
            childRunResult.stage = WorkflowStage.HEALTH_DETAILS
            healthReportFeedbackResult = self.insertHealthReport(result=childRunResult)
            self._log_feedback(healthReportFeedbackResult)
            if healthReportFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
                self.page.wait_for_timeout(30000)
                self._skip_child()
                childRunResult.feedback = healthReportFeedbackResult
                return childRunResult
            
            childRunResult.stage = WorkflowStage.FINAL_SUBMIT

            confirmClickBtn = self.page.get_by_role('button',name='Confirm & Submit')

            confirmClickBtn.click()
            self.synchronizer.wait_loading(page=self.page)
            # self.page.wait_for_timeout(1500)
            portalFeedback = PortalFeedbackDetector(self.page, success_msg="Child finally saved succesfully.")
            current_page_locator = self.page.get_by_role("heading", name="Screening Preview")
            next_page_locator = self.page.get_by_role("button", name="+ Add New Child")
            next_page_locator.wait_for(state="visible",timeout=1500)
            finalFeedbackResult: FeedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
            self._log_feedback(finalFeedbackResult)
            if finalFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
                logging.info(f"Error in finally saving this child.")
                self._skip_child()
                childRunResult.feedback = finalFeedbackResult
            childRunResult.feedback = finalFeedbackResult
            return childRunResult

        except Exception as e:
            logging.error(f"Can't save this child saving it to unsaved child with error message and moving to next: {e}")
            ## TODO save this non-saved child to our unsaved excel file
            self._skip_child()
            childRunResult.feedback = FeedbackResult(outcome=FeedbackOutcome.SYSTEM_ERROR, message="Internal Error happened. Moving to next child")
            return childRunResult


    