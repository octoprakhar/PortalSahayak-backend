from playwright.sync_api import Page,Locator,TimeoutError
from threading import Event
import logging



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
        
    def wait_for_setting_height_or_weight(self, page: Page):
        page.wait_for_function(
            """
            () => {
                // First group
                const anthropometry = [
                    document.querySelector('select[name="weightAgeClassification"]'),
                    document.querySelector('select[name="lengthAgeClassification"]'),
                    document.querySelector('select[name="weightHeightClassification"]')
                ];

                // Second group
                const bmi = [
                    document.querySelector('select[name="bmiClassification"]'),
                    document.querySelector('select[name="bmiResult"]')
                ];

                // Determine which complete group exists on the page
                let activeGroup;

                if (anthropometry.every(el => el !== null)) {
                    activeGroup = anthropometry;
                } else if (bmi.every(el => el !== null)) {
                    activeGroup = bmi;
                } else {
                    // No complete group yet
                    return false;
                }

                // Wait until every select in the active group has a value other than "0"
                return activeGroup.every(el => el.value !== "0");
            }
            """,
            timeout=15000,
        )
        
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
        