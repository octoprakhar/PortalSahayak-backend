from playwright.sync_api import Page,Locator

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