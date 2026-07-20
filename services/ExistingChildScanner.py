from playwright.sync_api import Page,Locator
import re
import logging
from all_models.ClassRange import ClassRange


class ExistingChildScanner:
    """
    This class will handle scanning and returning total_count, or list of children, who are eligible for screening at any point.
    """
    def __init__(self, page: Page,class_range: ClassRange | None, is_awc_screening: bool = True):
        self.page = page
        self.is_awc_screening = is_awc_screening
        self.class_range = class_range

    def _get_class(self,class_str: str)-> int:
        """
        Convert a string like 'Class 9' (with optional leading/trailing spaces)
        into the integer 9.
        """
        class_str = class_str.strip()
        return int(class_str.split()[-1])
    
    def _get_desired_table_present(self, table_column_names: list[str]) -> Locator|None:
        """
        It will check whether there is a table, with table column names are present.
        It will not return if that table has exact these column names, but returns if given
        all table columns names are present in a table
        """
        table = self.page.locator('table')

        for i in range(table.count()):
            table = table.nth(i)

            headers = (table.locator('th').all_text_contents())

            headers = [header.strip() for header in headers]

            if all(column in headers for column in table_column_names):
                return table
        
        return None

    def _go_to_initial_page(self):
        """
        When called it will take us to the first page
        """
        prev_button = self.page.get_by_role("button",name="Prev")

        while not prev_button.is_disabled():

            prev_button.click()

            ## Since it is not making any network call so might not need to wait
    
    def _go_to_next_page(self):

        next_button = self.page.get_by_role("button",name="Next")
        next_button.click()

    def _is_next_page_visible(self) -> bool:
        """
        It will check the next button if it is disable or not
        """
        next_btn = self.page.get_by_role("button",name="Next")
        return not next_btn.is_disabled()

    def _is_age_eligible(self, table_row: Locator, target_col_idx : int)-> bool:
        """
        Age will be of type "X years Y months"
        check X 
        """

        age_text = table_row.locator("td").nth(target_col_idx).inner_text().strip()
        

        match = re.search(r"(\d+)\s*years?", age_text)

        if not match:
            return False

        years = int(match.group(1))

        if self.is_awc_screening:
            return years < 6

        else:
            return years < 19


    def _is_start_screening_button_present(self, table_row: Locator, target_col_idx : int) -> bool:
        """
        Get that column where screening button could be present.
        Check whether there is a button with title = Start Screening
        """

        screening_cell = table_row.locator("td").nth(target_col_idx)

        return screening_cell.locator('[title="Start Screening"]').count() > 0
    
    def _is_child_in_class_range_present(self, table_row: Locator, target_col_idx: int) -> bool:
        """
        Get the class value and then check whether it lies in class range.
        """

        class_cell = table_row.locator("td").nth(target_col_idx)
        class_cell_text = class_cell.inner_text()
        class_value = self._get_class(class_str=class_cell_text)

        return class_value <= self.class_range.to_class and class_value >= self.class_range.from_class

    def get_total_existing_student(self) -> int:
        total_students = 0

        ## Check whether desired table is present or not
        # print("Checking whether desired table is present or not")
        desired_table = self._get_desired_table_present(table_column_names=["Gender","Name","Age"])

        if not desired_table:
            logging.info("No table found..")
            return 0
        
        # logging.info(f"Got desired table as {desired_table.inner_text()}")

        ## First go to first page
        self._go_to_initial_page()

        headers = [
            h.strip()
            for h in desired_table.locator("th").all_text_contents()
        ]

        age_col_idx = headers.index("Age")
        screening_btn_col_idx = headers.index("Screening Actions")


        if age_col_idx is None:
            raise ValueError("Age column not found")

        if screening_btn_col_idx is None:
            raise ValueError("Screening Actions column not found")
        
        if self.class_range:
            class_range_idx = headers.index("Class")
        
        # logging.info(f"Got age column index as: {age_col_idx}. and screening button index as: {screening_btn_col_idx}")

        ## Loop till next page is visible
        while True:
            desired_table = self._get_desired_table_present(
                table_column_names=["Gender", "Name", "Age"]
            )

            ## Now go for each rows

            rows = desired_table.locator('tbody tr')
            for i in range(rows.count()):
                row = rows.nth(i)
                if (self._is_age_eligible(table_row=row,target_col_idx=age_col_idx) and self._is_start_screening_button_present(table_row=row, target_col_idx=screening_btn_col_idx)):
                    # print(f"Got this row as eligible row: \n{row.inner_text()}")
                    ## Check whether class range is present, if class range is present, then just check for that if class range is present
                    if self.class_range:
                        # logging.info("Got class range")
                        
                        if self._is_child_in_class_range_present(table_row=row, target_col_idx=class_range_idx):
                            # logging.info(f"Child: \n{row.inner_text()}\nis present in the given class range")
                            total_students += 1
                                
                    else:
                        logging.info("Class range is none, but age, and start screening is valid, so just increasing it.")    
                        total_students += 1

                

                
            if not self._is_next_page_visible():
                break

            self._go_to_next_page()

        return total_students

        
        # print(f"total eligible counts as : {total_students}")