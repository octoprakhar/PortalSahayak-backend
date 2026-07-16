from playwright.sync_api import Page,Locator
import logging

from facility.model.ReferralDecision import ReferralDecision
from services.PageSynchronizer import PageSynchronizer

class FacilityManipulator:
    """
    This class will just try to select that facility name and type 
    """

    def __init__(self, page:Page, synchronizer: PageSynchronizer):
        self.page = page
        self.synchronizer = synchronizer

    def _get_referral_table(self)-> Locator | None:
        """
        Get the table with these four columns "Health Conditions	Health Condition Name	Facility Type	Facility Name"
        """
        tables = self.page.locator("table")

        for i in range(tables.count()):
            table = tables.nth(i)

            headers = [h.strip() for h in table.locator("thead th").all_text_contents()]

            expected = [
                "Health Conditions",
                "Health Condition Name",
                "Facility Type",
                "Facility Name"
            ]

            if all(any(exp in h for h in headers) for exp in expected):
                return table
            
        return None
    
    def _get_disease_row(self,disease_name: str, table: Locator) -> Locator | None:
        # Find the index of the "Health Condition Name" column
        headers = table.locator("thead th")
        header_count = headers.count()

        disease_col_index = None
        for i in range(header_count):
            header_text = headers.nth(i).inner_text().strip()
            if header_text == "Health Condition Name":
                disease_col_index = i
                break

        if disease_col_index is None:
            raise ValueError("Could not find 'Health Condition Name' column.")

        # Search each row for the disease name
        rows = table.locator("tbody tr")
        row_count = rows.count()

        for i in range(row_count):
            row = rows.nth(i)
            cell_text = (
                row.locator("td")
                .nth(disease_col_index)
                .inner_text()
                .strip()
            )

            if cell_text == disease_name:
                return row

        return None
    
    def _select_facility_type(self,disease_row: Locator,facility_type: str,facility_type_col_idx: int):
        # Get the Facility Type cell in this row
        cell = disease_row.locator("td").nth(facility_type_col_idx)

        # Click the react-select input
        input_box = cell.locator("input")
        input_box.click()

        # Type the facility type
        input_box.fill(facility_type)

        # Wait for dropdown to appear and click the option
        option = self.page.get_by_role("option", name=facility_type, exact=True)
        option.wait_for(state="visible")
        option.click()
        

    def _select_facility_name(self,disease_row: Locator, facility_name: str, facility_name_col_idx: int):
        # Get the Facility Name cell in this row
        cell = disease_row.locator("td").nth(facility_name_col_idx)

        # Click the react-select input
        input_box = cell.locator("input")
        input_box.click()

        # Type the facility name
        input_box.fill(facility_name)

        # Wait for dropdown to appear and click the option
        option = self.page.get_by_role("option", name=facility_name, exact=True)
        option.wait_for(state="visible",timeout=30000)
        option.click()

        
    def select_facility_type_and_name(self,referral_decision: ReferralDecision):
        """
        It will select the facility type and name for that specific disease
        """
        ## Step 1-> get refrerral table
        table = self._get_referral_table()
        if not table:
            raise RuntimeError("Cannot get any table to select facility for referral")

        # print(f"Got table as \n{table.inner_text()}")

        ## Step 2 -> get that specific rule from the table with disease name
        disease_row = self._get_disease_row(disease_name=referral_decision.disease_name,table=table)
        if not disease_row:
            raise RuntimeError(f"Cannot get disease:{referral_decision.disease_name} to select facility for referral")
        
        # print(f"got disease row as \n{disease_row.inner_text()}")

        ## Get facility type and facility name index
        headers = table.locator("thead th")
        header_count = headers.count()

        facility_type_col_index = None
        facility_name_col_index = None
        for i in range(header_count):
            text = headers.nth(i).inner_text().strip()

            if "Facility Type" in text:
                facility_type_col_index = i

            elif "Facility Name" in text:
                facility_name_col_index = i

            if (
                facility_type_col_index is not None
                and facility_name_col_index is not None
            ):
                break


        ## Step 3 => select that facility type
        

        ## Step 3.5, wait for facility name to reload
        self._select_facility_type(disease_row=disease_row,facility_type=referral_decision.facility_type,facility_type_col_idx=facility_type_col_index)

        ## Step 4 => select facility name
        self._select_facility_name(disease_row=disease_row,facility_name_col_idx=facility_name_col_index,facility_name=referral_decision.facility_name)