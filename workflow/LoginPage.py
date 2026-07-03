from playwright.sync_api import Page, Locator
import logging
from typing import Callable
from all_models.FeedbackResult import FeedbackResult,FeedbackOutcome
from services.PageSynchronizer import PageSynchronizer

class LoginPage:
    """
    This handles website login process and check whether it is logged in or not.
    Assuming we are on that specific page only to start filling login form

    """
    def __init__(self, page: Page, success_locator: Locator, synchronizer: PageSynchronizer):
        self.page = page
        self.success_locator = success_locator
        self.synchronizer = synchronizer


    def _fill_captcha(self):
        captcha = self.page.locator("span.select-none").inner_text()

        self.page.get_by_placeholder("Captcha").fill(captcha)

    def _get_login_response(self) -> dict:

        login_btn = self.page.get_by_role("button",name="Login")

        with self.page.expect_response(
            lambda response:
                "AuthenticateUser" in response.url
                and response.request.method == "POST"
        ) as response_info:
            login_btn.click()
        
        response = response_info.value

        try:
            return response.json()
        except Exception:
            logging.exception("Could not parse login response")
            return {}

    def get_authenticate_user_response(self,userName:str, password: str) -> dict:
        # print("Authenticated user response triggered")
        """
        When user logged in, there metadata can be got through response body of /authenticate user
        """
        # Step 1: fill userName
        
        self.page.get_by_placeholder("Username").fill(userName)

        # Step 2: Fill password
        self.page.get_by_placeholder("Password").fill(password)

        # Step 3 : fill captcha
        self._fill_captcha()

        ## Step 4: click login

        ## Check whether response came if not invalid credentials
        response_data = self._get_login_response()

        return response_data


    def login(self, userName: str, password: str) -> FeedbackResult:
        # Step 1: fill userName
        
        self.page.get_by_placeholder("Username").fill(userName)

        # Step 2: Fill password
        self.page.get_by_placeholder("Password").fill(password)

        # Step 3 : fill captcha
        self._fill_captcha()

        ## Step 4: click login

        ## Check whether response came if not invalid credentials
        response_data = self._get_login_response()

        if not response_data:
            return FeedbackResult(
                outcome=FeedbackOutcome.SYSTEM_ERROR,
                message="Could not parse login response"
            )

        if not response_data["succecced"]:
            return FeedbackResult(
                outcome=FeedbackOutcome.FAILURE,
                message=response_data["message"]
            )
        ## Check whether anything from next page is present or not
        try:
            ## First check whether spinner is present or not
            self.synchronizer.wait_loading(self.page)

            ## Then when spinner is not present check for next page
            self.success_locator.wait_for(
                state="visible",
                timeout=5000
            )
        except Exception as e:
            logging.exception(f"Error occured while checking for next screen in login page: \n{e}")
            return FeedbackResult(outcome=FeedbackOutcome.SYSTEM_ERROR, message="Server side error occured while logging in the user")
        
        return FeedbackResult(outcome=FeedbackOutcome.SUCCESS, message="Successfully Logged in user")

