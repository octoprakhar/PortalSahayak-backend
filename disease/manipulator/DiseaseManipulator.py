from playwright.sync_api import Page, Locator
import re
import logging

from disease.models.DiseaseDefinition import DiseaseDefinition
from disease.models.DiseaseCategory import DiseaseCategory
from services.PageSynchronizer import PageSynchronizer
class DiseaseManipulator:
    """
    This class will act as a body, to change the input values for the filling fields
    It doesn't know why to do it, it just know how to change them.
    """

    def __init__(self,page: Page, synchronizer: PageSynchronizer):
        self.page = page
        self.synchronizer = synchronizer

    def _is_question_checked(self, row: Locator) -> bool:
        checkbox = row.locator("input[type='checkbox']")
        return checkbox.is_checked()
    
    def _get_specific_category(self, category: DiseaseCategory):
        """
        click on the checkbox whether it is defect at birth, deficiecy, childhood disease, or developemental detail
        """
        category_mappers = {DiseaseCategory.DEFECTS_AT_BIRTH: "defects at birth", DiseaseCategory.DEFICIENCIES : "deficiencies", DiseaseCategory.DEVELOPMENTAL_DELAY: "development delay", DiseaseCategory.CHILDHOOD_DISEASES: "childhood diseases"}

        category_button = self.page.get_by_role(
            "button",
            name=re.compile(
                f"^{re.escape(category_mappers[category])}$",
                re.IGNORECASE
            )
        )

        category_button.wait_for(state="visible",timeout=3000)

        if category_button.count() > 0:
            category_button.click()
            return
        raise Exception("Not specific button found")

    def _select_disease_name_table(self)-> Locator:
        tables = self.page.locator("table")

        for i in range(tables.count()):
            table = tables.nth(i)

            headers = [h.strip() for h in table.locator("thead th").all_text_contents()]

            expected = [
                "Select",
                "Code",
                "Health Condition Name"
            ]

            if all(any(exp in h for h in headers) for exp in expected):
                return table
            
        return None
    
    def _select_question_name_table(self)-> Locator:
        tables = self.page.locator("table")

        for i in range(tables.count()):
            table = tables.nth(i)

            headers = [h.strip() for h in table.locator("thead th").all_text_contents()]

            expected = [
                "Select",
                "Checklist",
                "Question"
            ]

            if all(any(exp in h for h in headers) for exp in expected):
                return table
            
        return None
    
    def _select_disease_name(self,table: Locator, name: str):

        headers = [h.strip() for h in table.locator("thead th").all_text_contents()]
        column_index = headers.index("Health Condition Name")
        check_box_index = headers.index("Select")

        ## Get all disease name
        rows = table.locator("tbody tr")


        for i in range(rows.count()):
            row = rows.nth(i)

            cell = row.locator("td").nth(column_index)

            if cell.inner_text().strip() == name:
                checkbox = row.locator("td").nth(check_box_index)
                checkbox.click()

    def _select_question_name(self,table:Locator, name:str):
        headers = [h.strip() for h in table.locator("thead th").all_text_contents()]
        column_index = headers.index("Question")
        check_box_index = headers.index("Select")

        ## Get all disease name
        rows = table.locator("tbody tr")


        for i in range(rows.count()):
            row = rows.nth(i)

            cell = row.locator("td").nth(column_index)

            if cell.inner_text().strip() == name:
                checkbox = row.locator("td").nth(check_box_index)
                checkbox.click()
    
    def _get_disease_table_row(self,table: Locator, name: str)-> Locator | None:
        headers = [h.strip() for h in table.locator("thead th").all_text_contents()]
        column_index = headers.index("Health Condition Name")

        ## Get all disease name
        rows = table.locator("tbody tr")


        for i in range(rows.count()):
            row = rows.nth(i)

            cell = row.locator("td").nth(column_index)

            if cell.inner_text().strip() == name:
                return row
        return None


    def _get_question_table_row(self, table: Locator, name: str)-> Locator:
        headers = [h.strip() for h in table.locator("thead th").all_text_contents()]
        column_index = headers.index("Question")

        ## Get all disease name
        rows = table.locator("tbody tr")


        for i in range(rows.count()):
            row = rows.nth(i)

            cell = row.locator("td").nth(column_index)

            if cell.inner_text().strip() == name:
                return row
        return None
    
    def select_others_disease(self,disease:DiseaseDefinition):
        """
        THe diseases with others category are be found here.
        """
        other_div = self.page.locator('label:has-text("Other Health Condition")')
        checkbox = other_div.locator('input[type="checkbox"]')
        checkbox.check()

        referHealthFacility = self.page.locator('input[name="otherHealthConditionOption"][value="2"]')
        referHealthFacility.wait_for(state='visible',timeout=5000)
        referHealthFacility.check()

        otherDiseaseTextArea = self.page.locator('textarea[placeholder="Enter details (max 100 chars)"]')
        otherDiseaseTextArea.wait_for(state='visible',timeout=5000)
        otherDiseaseTextArea.fill(disease.name)

    def click_check_box(self,disease:DiseaseDefinition):
        ## Click the category button first
        self._get_specific_category(category=disease.category)
        
        ## Get disease table and check the disease
        target_table = self._select_disease_name_table()
        if not target_table:
            raise Exception("Can't get the target disease table")
        # print(target_table.inner_text())

        ## Select the disease
        self._select_disease_name(table=target_table, name=disease.name)
        
        ## Technically we don't need to select question boxes for this disease to show it down, so we can skip it for now

    def uncheck_box(self,disease:DiseaseDefinition):

        ## Step 1: get specific category
        self._get_specific_category(category=disease.category)

        ## Step: 2, check whether it's corresponding question is checked or not
        ## Get the row for the question

        ## Let's check whether boxes are checked or enabled or what
        target_table = self._select_question_name_table()

        if not target_table:
            # print("No target table for question found")
            return
        
        # print("Got target table value as \n\n")
        print(target_table.inner_text())

        questions = disease.questions
        # print("======================")
        # print(f"Now let's search for these questions: \n{questions}")
        if questions:
            for question in questions:
                row = self._get_question_table_row(table=target_table,name=question.text)
                if not row:
                    # print("No row found")
                    return
                # print(f"\n")
                # print(f"Got row for question as : \n{row.inner_text()}")
                is_checkbox_checked = self._is_question_checked(row=row)
                # print(f"Is checkbox for this question checked: {is_checkbox_checked}")
                if is_checkbox_checked:
                    self._select_question_name(table=target_table, name=question.text)

        
        # print("\nall questions get unclicked")
        

        # ## Start unclicking the disease
        disease_target_table = self._select_disease_name_table()
        # print(f"\nGot disease table as: \n{disease_target_table.inner_text()}")

        
        self._select_disease_name(table=disease_target_table, name=disease.name)

        ## Cheked is actually important to me maybe enabled is not that much, is it enabled or not must not be the problem, it 
        ## is the problem for removal or addition strategies

    def set_height(self,new_height: str):
        height_input = self.page.locator("input[name='height']")
        height_input.fill(new_height)
        self.synchronizer.wait_for_setting_height_or_weight(page=self.page)

    def set_weight(self,new_weight: str):
        weight_input = self.page.locator("input[name='weight']")
        weight_input.fill(new_weight)
        self.synchronizer.wait_for_setting_height_or_weight(page=self.page)

    def set_head_circumference(self,new_head_circumference: str):
        head_circumference_input = self.page.locator("input[name='headCircumference']")
        head_circumference_input.fill(new_head_circumference)
        self.synchronizer.wait_for_setting_head_circumference(page=self.page)

    def set_hb(self,new_hb: str):
        hb_input = self.page.locator("input[name='hb']")
        hb_input.fill(new_hb)

    def get_height(self)->float | None:
        height = self.page.locator('input[name="height"]').input_value()
        try:
            return float(height)
        except:
            return None
        
    def get_weight(self)->float | None:
        weight = self.page.locator('input[name="weight"]').input_value()
        try:
            return float(weight)
        except:
            return None
    
    def get_head_circumference(self)->int | None:
        
        self.synchronizer.wait_for_setting_head_circumference(page=self.page)

        head_circumference = self.page.locator('input[name="headCircumference"]').input_value()
        try:
            return int(float(head_circumference))
        except Exception as e:
            logging.error(
                f"Head circumference conversion failed: {e}"
            )
            return None
        
    def get_hb(self)->float | None:
        hb = self.page.locator('input[name="hb"]').input_value()
        try:
            return float(hb)
        except:
            return None
    
        