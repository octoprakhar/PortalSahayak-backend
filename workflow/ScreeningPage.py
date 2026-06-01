# To use this class after creating browser instant, and entering in the "Adding" page
# This class is simply saying "give me the page object, and the child and I will save it"
import logging
from datetime import datetime

from playwright.sync_api import Page,Locator
from all_models.child_models import Child
from utils.loaderUtils import get_age

class ChildScreeningPage:
    def __init__(self, page:Page, child:Child):
        self.page = page
        self.child = child
        self.age = get_age(self.child.dob)


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
    
    def select_facility(self, facility_type, facility_name):

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
        facility_name_input = referral_section.locator(
            'input[role="combobox"]'
        ).nth(1)

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


    def insertPersonalDetails(self):
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
        genderDropDown.select_option(label=self.child.gender)
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

    def insertHealthReport(self):
        heightField = self.page.locator('[name="height"]')
        weightField = self.page.locator('[name="weight"]')
        headCircumField = self.page.locator('[name="headCircumference"]')
        hbField = self.page.locator('[name="hb"]')
        

        heightField.fill(self.child.height)
        weightField.fill(self.child.weight)
        headCircumField.fill(self.child.headCircumference)
        hbField.fill(self.child.hb)

        if round(self.age,1) >= 0.6:
            muacFIeld = self.page.locator('[name="muac"]')
            muacFIeld.fill("13")

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
            self.select_facility(self.child.facilityType,self.child.facilityName)

        finalSubmitBtn = self.page.get_by_role('button',name='Preview & Submit')
        self.page.wait_for_timeout(5000)
        finalSubmitBtn.click()

    def saveExistingChild(self, existingChildLocator: Locator = None):

        """
        It saves the existing child, if you give no locator, we will take self.child details and then try getting that child from table 
        """

        if existingChildLocator is None:
            ## Use self.child to get the details
            rows = self.page.locator("table > tbody > tr")

            editChildButton = None

            target_name = self.child.name.strip().lower()
            target_father = self.child.fatherName.strip().lower()

            for i in range(rows.count()):

                row = rows.nth(i)

                name = (
                    row.locator("td")
                    .nth(2)
                    .inner_text()
                    .strip()
                    .lower()
                )

                father_name = (
                    row.locator("td")
                    .nth(6)
                    .inner_text()
                    .strip()
                    .lower()
                )

                if (
                    name == target_name
                    and father_name == target_father
                ):

                    logging.info(
                        f"Matched child row: {name} / {father_name}"
                    )

                    editChildButton = row.locator(
                        'div[title="Start Screening"]'
                    )

                    break

            if editChildButton is None:

                raise Exception(
                    f"Could not find child "
                    f"{self.child.name}"
                )
        else:
            editChildButton = (
            existingChildLocator
            .locator('div[title="Start Screening"]')
            )
        


        


        editChildButton.click()

        self.page.wait_for_load_state("networkidle")

        self.insertHealthReport()

        self.page.wait_for_timeout(1500)

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

        


    

    def submit(self):

        ## Add child's personal detail and then add it's health report of each child, and then go

        ## For each child
        try:
            self.insertPersonalDetails()
            self.insertHealthReport()

            confirmClickBtn = self.page.get_by_role('button',name='Confirm & Submit')
            confirmClickBtn.click()

        except Exception as e:
            logging.error(f"Can't save this child saving it to unsaved child with error message and moving to next: {e}")
            ## TODO save this non-saved child to our unsaved excel file


    