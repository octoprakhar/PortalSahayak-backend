from playwright.sync_api import Page
import logging

from all_models.InstitutionData import InstitutionData
from constants.institution_type import InstitutionType

from utils.datetimeUtils import iso_to_ddmmyyyy,date_to_month_year

class InstitutionSelectionPage:

    """
    This class will handle all the workflows regarding institution selection page
    like selecting the month, or selecting the particular institution.

    Parameter:
    date: str = This date will be ISO string, we will change it the way we want
    page: Page = playwright page instance, where we need to do the workflow
    """
    def __init__(self,page: Page, date: str):
        self.page = page
        self.date = date


    def _get_all_institution_response(self) -> dict:
        """
        When we click on search button after selecting the month, it will track and get all responses for that.

        Parameters:
        None

        Returns:
        institution_data: dict | None => just Return the data of the response
        """
        search_btn = self.page.get_by_role("button",name="Search")
        with self.page.expect_response(
            lambda response:
                "MicroPlan" in response.url
                and response.request.method == "POST"
        ) as response_info:
            search_btn.click()
        
        response = response_info.value

        try:
            return response.json()
        except Exception as e:
            logging.exception(f"Exception occured while reading response of all institutions: \n{e}")
            return {}
        
    def _map_to_institutions(
        self,
        response_data: dict
    ) -> list[InstitutionData]:

        institutions = []

        for item in response_data.get("data", []):

            institutions.append(
                InstitutionData(
                    institution_plan_id=item["PlanID"],
                    institution_name=item["Institution_Name"],
                    institution_type=InstitutionType(
                        item["Institution_Type_Name"].lower()
                    ),
                    planned_date=item["Visit_Date"]
                )
            )

        return institutions

    def _institution_attendance(self, institution_data: InstitutionData, is_ANM_present: bool = True):
        """
        If attendance for that institution is not there then just do that thing. Ideally 
        in each team there will be doctors and ANM, let's just say maybe if ANM is not there
        So we don't need to click the radio button in front of ANM's name.

        Parameters:
        name: Str = Institutions Name
        is_ANM_present: str = Whether or not ANM was there while screening this institution or not

        Returns:
        None
        """
        pass

    def _get_institutions_by_date(self, all_institutions: list[InstitutionData]) -> list[InstitutionData]:
        """
        It will just return required institution for that date

        Parameters:
        all_institutions: list[InstitutionData] = Reponse of all institution for that month

        Returns:
        All institution planned for that day
        """
        formatted_date = iso_to_ddmmyyyy(self.date)
        return [
            institution
            for institution in all_institutions
            if institution.planned_date == formatted_date
        ]

    def get_month_data(self) -> list[InstitutionData]:
        """
        This will help in selection of the month in which we had the institution 
        that we need to do the screening work. and also returns all the institutions data 
        for that date.

        Returns:
        list[InstitutionData]
        """
        try:
            ##Step 1: Select the month and then click select, 
            month = date_to_month_year(self.date)
            self.page.locator('[name="financialMonth"]').select_option(label=month)
            self.page.get_by_role('button',name='Search').click()

            ## If can't select that specific date / month throw error "Invalid Date was given"

            #Step 2:  wait for API response, change api response in format
            all_instititution_response = self._get_all_institution_response()

            if not all_instititution_response:
                raise Exception("Could not parse response data")

            ## If no response then throw error "No institution found"

            ## Change it to Institution data formation
            institution_data = self._map_to_institutions(all_instititution_response)


            ## Step 3: Get all the institution data for that date
            required_institution = self._get_institutions_by_date(all_institutions=institution_data)

            ## If no institution is there for that date, then simply throw error as  "No institution found for that date"

            ## Return the List[InstitutionData] back
            return required_institution
        except Exception as e:
            logging.exception(f"Error occured while trying to select the month in screening page: \n{e}")
            raise Exception("Error occured while trying to open the monthly screening data")
        
    def select_institution(self,institution_data:InstitutionData, is_ANM_present: bool = True):
        try:

            ## step 2: Check whether attendance for institution is already done(it means it was already screening), or we need to do it
            is_attendance_popup_shown = self.page.locator().is_visible()

            ## If attendance not done, do the attendance stuff
            if not is_attendance_popup_shown:
                self._institution_attendance(institution_data=institution_data, is_ANM_present=is_ANM_present)

            ## Click final button to start screening
            pass
        except Exception as e:
            logging.exception(f"Error occured while trying to select the given institution name: \n{e}")
            raise Exception("Error occured while trying to open the institution")