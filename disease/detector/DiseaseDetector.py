from playwright.sync_api import Page,Locator

from disease.models.DetectedDisease import DetectedDisease
from disease.repository.DiseaseRepository import DiseaseRepository
from disease.models.DiseaseDefinition import DiseaseDefinition
from disease.models.DiseaseSource import DiseaseSource
from disease.models.DiseaseCategory import DiseaseCategory

class DiseaseDetector:
    """
    It's main job is to just go on that page, and check
    the section when we refer the child and get all the 
    diseases that are shown there, just the list of all the diseases
    """

    def __init__(self, page:Page):
        self.page = page
        self.diseaseRepository = DiseaseRepository()

    def _get_table(self) -> Locator | None:
        """
        It will return the table where actual
        data is present for diseases
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
    
    def _get_health_condition_name(self, table: Locator) -> list[str]:
        ## Get all the headers of that table
        headers = [h.strip() for h in table.locator("thead th").all_text_contents()]


        ## Get the column index of column: "Health Condition Name", so we could map each rows
        column_index = headers.index("Health Condition Name")

        ## Get all disease name
        rows = table.locator("tbody tr")

        diseases = []

        for i in range(rows.count()):
            row = rows.nth(i)

            cell = row.locator("td").nth(column_index)

            diseases.append(cell.inner_text().strip())

        return diseases
    
    def _change_disease_definitions_to_defected_diseases(self,diseases: list[DiseaseDefinition]) -> list[DetectedDisease]:
        """
        Just give source to UNKNOWN coz we don't know about the source for now
        """
        detected_diseases = []
        for disease in diseases:
            detected_diseases.append(DetectedDisease(definition=disease,source=DiseaseSource.UNKNOWN))
        
        return detected_diseases


    def detect(self) -> list[DetectedDisease]:
        ## First get that table if present
        required_table = self._get_table()
        if not required_table or required_table is None:
            # print("No table found")
            return []
        # print(f"Got table for diseases as this \n{required_table.inner_text()}")
        
        ## If we found that row, then next work is simple, getting the disease name
        health_condition_names = self._get_health_condition_name(table=required_table)
        # print(f"Got health condition names as : {health_condition_names}")

        # print("========================")
        if not health_condition_names:
            # print("We got the table, but can't get the health condition name")
            return []
        
        # print(f"Got health condition names as : {health_condition_names}")

        ## Now get disease by name for all the list of diseases
        all_diseases = []
        for condition in health_condition_names:
            full_condition_data = self.diseaseRepository.get_by_name(condition)
            if not full_condition_data:
                ## It means this disease is in others, and it could be selected by the user, so we need to make disease definition for it.
                all_diseases.append(DiseaseDefinition(name=condition, code=None, category= DiseaseCategory.OTHERS, questions=[]))
                continue
            all_diseases.append(full_condition_data)

        # print("==============================")
        # print(f"got all the diseases with metadata as: {all_diseases}")

        ## Now change those diseases to Defected disease class with DiseaseSource.UNKNOWN, because in the starting we don't know whether it is 
        # having what source
        if not all_diseases:
            return []
        
        return self._change_disease_definitions_to_defected_diseases(diseases=all_diseases)
        


        
