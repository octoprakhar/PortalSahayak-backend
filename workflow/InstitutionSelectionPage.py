from playwright.sync_api import Page
import logging

from all_models.InstitutionData import InstitutionData
from constants.institution_type import InstitutionType
from services.PageSynchronizer import PageSynchronizer

from utils.datetimeUtils import iso_to_ddmmyyyy,date_to_month_year

class InstitutionSelectionPage:

    """
    This class will handle all the workflows regarding institution selection page
    like selecting the month, or selecting the particular institution.

    Parameter:
    date: str = This date will be ISO string, we will change it the way we want
    page: Page = playwright page instance, where we need to do the workflow
    """
    def __init__(self,page: Page, date: str, synchronizer: PageSynchronizer):
        self.page = page
        self.date = date
        self.sychronizer = synchronizer


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

    def _institution_attendance(
        self,
        institution_data: InstitutionData,
        is_ANM_present: bool = True
    ):
        """
        Mark attendance for all team members.

        If ANM is not present, skip all ANM cards.
        """

        print("Starting attendance work")

        popup = self.page.get_by_role(
            "heading",
            name="Mark Attendance to Start Screening"
        ).locator(
            "xpath=ancestor::*[contains(@class,'fixed')]"
        )

        cards = popup.locator(
            "div.cursor-pointer:has(span.font-medium)"
        )

        count = cards.count()
        print(f"Got count of cards as: {count}")

        for i in range(count):
            card = cards.nth(i)

            role = card.locator("p.text-slate-500").inner_text().strip()

            if not is_ANM_present and "ANM" in role.upper():
                continue

            print("Clicking:", card.inner_text())

            card.click()

        popup.get_by_role(
            "button",
            name="Submit & Start"
        ).click()

        print("Attendance submitted")

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
    
    def _select_institution_by_name_and_date(
        self,
        institute_name: str,
        visit_date: str,
    ) -> bool:
        page = self.page

        visit_format_date = iso_to_ddmmyyyy(visit_date)


        while True:
            page.wait_for_selector("table tbody tr")

            # Only rows containing the institution name
            candidate_rows = page.locator(
                f'table tbody tr:has-text("{institute_name}")'
            )

            candidate_count = candidate_rows.count()


            for i in range(candidate_count):
                row = candidate_rows.nth(i)

                row_text = row.inner_text()


                # Verify date also matches
                if visit_format_date not in row_text:
                 continue


                # Prefer Start Screening
                for title in ("Start Screening", "View Students"):
                    button = row.locator(f'[title="{title}"]')

                    if button.count() > 0:
                        print(f"Clicking '{title}'")

                        button.first.scroll_into_view_if_needed()
                        button.first.click()

                        return True


            # Pagination
            next_btn = page.get_by_role("button", name="Next")

            if next_btn.count() == 0 or not next_btn.is_enabled():
                break

            next_btn.click()

            # Better than wait_for_timeout()
            page.wait_for_load_state("networkidle")


        return False
    

    def get_month_data(self) -> list[InstitutionData]:
        """
        This will help in selection of the month in which we had the institution 
        that we need to do the screening work. and also returns all the institutions data 
        for that date.

        Returns:
        list[InstitutionData]
        """
        try:
            ## Wait for loading to complete
            self.sychronizer.wait_loading(self.page)
            mht_select = self.page.locator("select[name=mht]")
            self.sychronizer.wait_for_institution_page_ready(mht_select=mht_select)
            ##Step 1: Select the month and then click select, 
            month = date_to_month_year(self.date)
            self.page.locator('[name="financialMonth"]').select_option(label=month)
            # self.page.get_by_role('button',name='Search').click()

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
            logging.exception(f"InstitutionSelectionPage: Error occured while trying to select the month in screening page")
            raise
        
    def select_institution(self,institution_data:InstitutionData, is_ANM_present: bool = True):
        try:

            # Step 1: select institution by name
            self._select_institution_by_name_and_date(institute_name=institution_data.institution_name, visit_date=institution_data.planned_date)

            print("Now checking for the attendance block...")
            ## step 2: Check whether attendance for institution is already done(it means it was already screening), or we need to do it
            self.sychronizer.wait_loading(page=self.page)
            is_attendance_popup_shown = self.page.get_by_role("heading",name="Mark Attendance to Start Screening").is_visible()
            print(f"Is attendance page visible: {is_attendance_popup_shown}")
            ## If attendance not done, do the attendance stuff
            if is_attendance_popup_shown:
                print("Trying to mark Attendance")
                self._institution_attendance(institution_data=institution_data, is_ANM_present=is_ANM_present)

        except Exception as e:
            # print(str(e))
            logging.exception(f"Error occured while trying to select the given institution name: \n{e}")
            print(e)
            raise Exception("Error occured while trying to open the institution")