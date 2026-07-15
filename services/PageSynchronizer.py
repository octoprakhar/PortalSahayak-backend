from playwright.sync_api import Page,Locator,TimeoutError
from threading import Event
import logging

from facility.constants.FacilityLoadResult import FacilityLoadResult


class PageSynchronizer:
    """
    This class will help us to check whether if we are working on the correct page or not.
    Especially the time of loading, coz maybe if loading is present and we try to do the checking
    it will fail
    """

    def wait_loading(self, page: Page):
        try:
            spinner = page.locator('[role="status"]')

            while spinner.count() > 0:
                for i in range(spinner.count()):
                    try:
                        spinner.nth(i).wait_for(
                            state="hidden",
                            timeout=180000
                        )
                    except:
                        pass

                if spinner.filter(visible=True).count() == 0:
                    break

        except Exception:
            pass
    def wait_for_institution_page_ready(self, mht_select: Locator):
        try:
            mht_select.page.wait_for_function(
                """
                (selector) => {
                    const select = document.querySelector(selector);
                    return select && select.options.length > 1;
                }
                """,
                arg="select[name='mht']",
                timeout=30000,
            )
        except TimeoutError:
            raise Exception("Institution dropdown was not populated.")
        
    def wait_for_setting_height_or_weight(self,page:Page):
        page.wait_for_function("""
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
                        """, timeout=15000)
        
    def wait_for_setting_head_circumference(self,page:Page):
        page.wait_for_function("""
            () => {
                const el = document.querySelector('select[name="headCircumferenceClassification"]');
                return el && el.value !== '0';
            }
            """)
        
    def wait_for_setting_blood_pressure(self,page:Page):
        page.wait_for_function("""
            () => {
                const el = document.querySelector('select[name="bloodPressureClassification"]');
                return el && el.value !== '0';
            }
            """)
    
    def wait_for_all_toast_disappear(
        self,
        page: Page,
        timeout: int = 15000,
    ):
        """
        Wait until all visible Toastify notifications disappear.

        Handles success, error, warning, info, etc.
        """

        try:
            page.wait_for_function(
                """
                () => {
                    return document.querySelectorAll(
                        '.Toastify__toast[data-in="true"]'
                    ).length === 0;
                }
                """,
                timeout=timeout,
            )
        except TimeoutError:
            raise Exception("Toast notification(s) did not disappear.")
        
    def click_and_wait_for_facility_reload(
        self,
        option: Locator,
        page: Page,
        cache_check_timeout_ms: int = 1000,
        response_timeout_ms: int = 10000,
    ):

        request_happened = Event()

        def on_request(req):
            if (
                "Hierarchy_Master/Get_HierarchyMaster" in req.url
                and req.method == "POST"
                and (req.post_data_json or {}).get("masterType") == 11
            ):
                request_happened.set()

        page.on("request", on_request)

        try:
            with page.expect_response(
                lambda r: (
                    "Hierarchy_Master/Get_HierarchyMaster" in r.url
                    and r.request.method == "POST"
                    and (r.request.post_data_json or {}).get("masterType") == 11
                ),
                timeout=response_timeout_ms,
            ) as response_info:

                option.click()

                # Allow cache case to reveal itself
                if not request_happened.wait(cache_check_timeout_ms / 1000):
                    return FacilityLoadResult.CACHE

            response = response_info.value

        except TimeoutError:
            if not request_happened.is_set():
                return FacilityLoadResult.CACHE

            raise TimeoutError(
                "Facility request was sent but response did not arrive."
            )

        finally:
            page.remove_listener("request", on_request)

        body = response.json()

        if not body.get("data"):
            return FacilityLoadResult.EMPTY

        return FacilityLoadResult.SERVER