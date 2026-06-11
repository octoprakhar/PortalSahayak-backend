# To use this class after creating browser instant, and entering in the "Adding" page
# This class is simply saying "give me the page object, and the child and I will save it"
import logging
from datetime import datetime
from playwright.sync_api import Page,Locator
from zoneinfo import ZoneInfo
import random
import time


from all_models.child_models import Child
from services.PortalFeedbackDetector import PortalFeedbackDetector
from services.SearchStudent import SearchStudent
from services.JobManager import JobManager
from all_models.FeedbackResult import FeedbackResult,FeedbackOutcome
from constants.log_type import LogType
from all_models.JobLogs import JobLog
from utils.loaderUtils import get_age,get_corrected_values
from services.SamManager import SamManager

class ChildScreeningPage:
    def __init__(self, page:Page, child:Child,sam_manager : SamManager, job_id: str = None):
        self.page = page
        self.child = child
        self.job_id = job_id
        self.sam_manager = sam_manager
        self.age = get_age(self.child.dob)
        self.is_to_select_nrc = False

    def select_disease(self,disease_name):

        ## Disease name for a child (a nullable column) must be get from excel
        tabs = [
            "Defects at Birth",
            "Deficiencies",
            "Childhood Diseases",
            "Development Delay"
        ]

        for tab in tabs:
            self.page.get_by_role("button", name=tab).click()

            self.page.wait_for_timeout(1000)

            row = self.page.locator("tr").filter(has_text=disease_name)

            if row.count() > 0:
                row.locator('input[type="checkbox"]').click()

                return True
        
        return False
    
    def select_facility(self, facility_type, facility_name, can_add_sam: bool):

        ## TODO Is SAM present
        refer_checkbox = self.page.locator('#referSameInstitute')
        refer_checkbox.check()

        referral_section = self.page.locator("div").filter(
            has_text="Refer to same facility for all Health Conditions"
        )

    # -----------------------------
    # FACILITY TYPE
    # -----------------------------
        facility_type_input = referral_section.locator(
            'input[role="combobox"]'
        ).first
        facility_name_input = referral_section.locator(
            'input[role="combobox"]'
        ).nth(1)

        if can_add_sam:
            facility_type_input.click()
            facility_type_input.fill("NRC")
            option = self.page.get_by_role(
                "option",
                name="NRC",
                exact=True
            ).first

            option.wait_for(state="visible")

            logging.info(
                f"Selecting facility type: {option.text_content()}"
            )

            option.click()
            facility_name_input.click()
            facility_name_input.fill("NRC DH BALAGHAT (NRC)")
            option = self.page.get_by_role(
                "option",
                name="NRC DH BALAGHAT (NRC)",
                exact=True
            ).first

            option.wait_for(state="visible")

            logging.info(
                f"Selecting facility name: {option.text_content()}"
            )

            option.click()
            
        else:
            facility_type_input.click()
            
            facility_type_input.fill(facility_type)

            option = self.page.get_by_role(
                "option",
                name=facility_type,
                exact=True
            ).first

            option.wait_for(state="visible")

            logging.info(
                f"Selecting facility type: {option.text_content()}"
            )

            option.click()

        

    # -----------------------------
    # FACILITY NAME
    # -----------------------------
        

            facility_name_input.click()
            facility_name_input.fill(facility_name)

            option = self.page.get_by_role(
                "option",
                name=facility_name,
                exact=True
            ).first

            option.wait_for(state="visible")

            logging.info(
                f"Selecting facility name: {option.text_content()}"
            )

            option.click()

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

        JobManager.add_log(
            self.job_id,
            JobLog(
                timeStamp=datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).isoformat(),
                type=log_type,
                message=message
            )
        )

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



    def insertPersonalDetails(self) -> FeedbackResult:
        ## We will take it from loaded excel his name, father's name, mother's name, DOB, address, mobile number
        ## Then perform this 
        self.page.get_by_role('button',name="Add New Child").click()

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

        ## Saving age as global variable

        if float(ageField.input_value()) < 1:
            birthWeightField = self.page.locator('[name="birthWeight"]')
            birthWeightField.fill("2500")
    

        logging.info("Please press enter to move forward....")

        saveChildBtn = self.page.get_by_role('button',name='Save & Start Screening')
        saveChildBtn.click()

        # Waiting and detecting if success and failure by UI
        self.page.wait_for_timeout(1500)
        portalFeedback = PortalFeedbackDetector(self.page,success_msg="Successfully inserted child detail")
        current_page_locator = self.page.get_by_role("heading", name="👨‍👩‍👧‍👦 Personal & Family Details")
        next_page_locator = self.page.get_by_role("heading", name="Screening for Health Conditions")

        feedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
        return feedbackResult
        # return FeedbackResult()


    def insertHealthReport(self) -> FeedbackResult:
        heightField = self.page.locator('[name="height"]')
        weightField = self.page.locator('[name="weight"]')
        hbField = self.page.locator('[name="hb"]')
        

        # random_number = random.randint(0, 9)
        # if random_number >= 5:
        heightField.fill(self.child.height)
        
        weightField.fill(self.child.weight)

        hbField.fill(self.child.hb)

        ## Check if child is SAM if yes, then check can we can't add it to SAM then just change it.
        can_add_sam = self.sam_manager.can_accept_sam()

        is_child_sam = False

        

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
        
        ## Checking for referal checkbox first time after height and weight fill
        referral_checkbox = self.page.locator('#referSameInstitute')
        
        
        ## Sam checking only when referal checkbox is available
        if referral_checkbox.is_visible():
            referral_table = self.page.locator(
                "table:has(th:text-is('Facility Type'))"
            )


            

            # logging.info(f"Got logs for referal table as as: {referral_table.inner_text()}")
            table_text = referral_table.inner_text()

            is_child_sam = "SAM" in table_text


            if is_child_sam and not can_add_sam:
                logging.info(f"We cannot add this child : {self.child.name} in SAM, because limit exceeds.")
                new_weight, new_height = get_corrected_values(self.age)
                logging.info(f"Setting new weight and height of child as :{new_weight,new_height}")
                heightField.fill(str(new_height))
        
                weightField.fill(str(new_weight))
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

            self.is_to_select_nrc = is_child_sam and can_add_sam
            

        if round(self.age,2) <= 5:
            headCircumField = self.page.locator('[name="headCircumference"]')
            headCircumField.fill(self.child.headCircumference)

        if round(self.age,1) >= 0.6 and round(self.age,2) <= 5:
            muacFIeld = self.page.locator('[name="muac"]')
            muacFIeld.fill("13")

        if round(self.age,2) > 5:
            # Fill vision Left
            self.page.locator('select[name="visionLeft"]').select_option(
                label=str(self.child.visionLeft)
            )

            # Fill vision Right
            self.page.locator('select[name="visionRight"]').select_option(
                label=str(self.child.visionRight)
            )

        ## Any disease selection
        disease_name = self.child.diseaseName
        if disease_name:
            isDiseaseSelected:bool = self.select_disease(disease_name=disease_name)
            if not isDiseaseSelected and disease_name != 'nan':
                other_div = self.page.locator('label:has-text("Other Health Condition")')
                checkbox = other_div.locator('input[type="checkbox"]')
                checkbox.check()

                referHealthFacility = self.page.locator('input[name="otherHealthConditionOption"][value="2"]')
                referHealthFacility.wait_for(state='visible',timeout=5000)
                referHealthFacility.check()

                otherDiseaseTextArea = self.page.locator('textarea[placeholder="Enter details (max 100 chars)"]')
                otherDiseaseTextArea.wait_for(state='visible',timeout=5000)
                otherDiseaseTextArea.fill(disease_name)


            
        else:
            logging.info(f"No disease for {self.child.name}, skipping selection")
        # self.select_disease(disease_name=disease_name)
        self.page.wait_for_timeout(1000)
        

        ## Select facility only when visible, it could not be visible if child is healthy
        referral_checkbox = self.page.locator('#referSameInstitute')

        if referral_checkbox.is_visible():
            logging.info(f"Calling Selecting facility for child: {self.child.name}, and to select nrc as : {self.is_to_select_nrc}, and is this child sam: {is_child_sam}")
            self.select_facility(facility_type=self.child.facilityType,facility_name=self.child.facilityName,can_add_sam=self.is_to_select_nrc)

        finalSubmitBtn = self.page.get_by_role('button',name='Preview & Submit')
        # self.page.wait_for_timeout(5000)
        finalSubmitBtn.click()
        self.page.wait_for_timeout(1000)
        portalFeedback = PortalFeedbackDetector(self.page, success_msg="Succesfully saved child health detail, moving to final submission.")
        current_page_locator = self.page.get_by_role("heading", name="Screening for Health Conditions")
        next_page_locator = self.page.get_by_role("heading", name="Screening Preview")
        feedbackResult: FeedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
        return feedbackResult



    def saveExistingChild(self, existingChildLocator: Locator = None) -> FeedbackResult:
        """
        Saves the existing child.
        If no locator is provided, locate the row using self.child details.
        """

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
            JobManager.add_log(
            self.job_id,
            JobLog(
                timeStamp=datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).isoformat(),
                type=LogType.INFO,
                message=f"{self.child.name} C/o- {self.child.fatherName} : is already exist."
            )
        )


        ## Check if target of students are completed then just press 'Yes proceed button automatically'
        
        message = self.page.get_by_text(
            "Planned children for this institution have been screened. Do you want to screen more?",
            exact=True
        )

        if message.is_visible():
            self.page.get_by_role("button", name="Yes, proceed!").click()
            

        self.page.wait_for_load_state("networkidle")

        healthReportFeedbackResult = self.insertHealthReport()
        self._log_feedback(healthReportFeedbackResult)
        if healthReportFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
            self._skip_child()
            return healthReportFeedbackResult
        # self.page.wait_for_timeout(1500)

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

        portalFeedback = PortalFeedbackDetector(self.page, success_msg="Sucessfully saved existing child's detail")
        current_page_locator = self.page.get_by_role("heading", name="Screening Preview")
        next_page_locator = self.page.get_by_role("button", name="+ Add New Child")
        finalFeedbackResult: FeedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
        self._log_feedback(finalFeedbackResult)
        if finalFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
            self._skip_child()
        return finalFeedbackResult


        


    

    def submit(self) -> FeedbackResult:

        ## If child is above 6years and It is awc don't enter here
        if self.age > 6:
            logging.info(f"📢📢 Got child of name: {self.child.name} has age greater than 6 and we are doing AWC so leaving.")
            return FeedbackResult(outcome=FeedbackOutcome.INVALID_DATA, message=f"Got child of name: {self.child.name} has age greater than 6 and we are doing AWC so leaving.")
        ## Add child's personal detail and then add it's health report of each child, and then go


        ## For each child
        try:
            logging.info("🎁🎁🎁Started the process of initial saving of child detail.")
            registerFeedbackResult = self.insertPersonalDetails()
            self._log_feedback(registerFeedbackResult)
            if registerFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
                self._skip_child()
                return registerFeedbackResult
            
            logging.info("🎁🎁🎁Started the process of health report saving of child detail.")

            healthReportFeedbackResult = self.insertHealthReport()
            self._log_feedback(healthReportFeedbackResult)
            if healthReportFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
                self._skip_child()
                return healthReportFeedbackResult

            confirmClickBtn = self.page.get_by_role('button',name='Confirm & Submit')

            confirmClickBtn.click()
            self.page.wait_for_load_state('networkidle')
            self.page.wait_for_timeout(1000)
            portalFeedback = PortalFeedbackDetector(self.page, success_msg="Child finally saved succesfully.")
            current_page_locator = self.page.get_by_role("heading", name="Screening Preview")
            next_page_locator = self.page.get_by_role("button", name="+ Add New Child")
            finalFeedbackResult: FeedbackResult = portalFeedback.check(current_screen_target=current_page_locator, next_screen_target=next_page_locator)
            self._log_feedback(finalFeedbackResult)
            if finalFeedbackResult.outcome == FeedbackOutcome.SUCCESS:
                if self.is_to_select_nrc:
                    logging.info(f"Selecting NRC for this child {self.child.name}")
                    self.sam_manager.register_sam()
            if finalFeedbackResult.outcome is not FeedbackOutcome.SUCCESS:
                logging.info(f"Error in finally saving this child.")
                self._skip_child()
            return finalFeedbackResult

        except Exception as e:
            logging.error(f"Can't save this child saving it to unsaved child with error message and moving to next: {e}")
            ## TODO save this non-saved child to our unsaved excel file
            self._skip_child()
            return FeedbackResult(outcome=FeedbackOutcome.SYSTEM_ERROR, message="Internal Error happened. Moving to next child")


    