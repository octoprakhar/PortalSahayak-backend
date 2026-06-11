from playwright.sync_api import Page,Locator
from all_models.FeedbackResult import FeedbackResult, FeedbackOutcome
import logging


class PortalFeedbackDetector:
    """
    This class is very important regarding detecting that whether portal has thrown any error type thing or not.
    Like if there is a popup of success, or failure, if failure then is there any validation failures, like 
    in bottom of any field, is there nay thing like "this field is required" type something is written it will be in 
    validation failure.
    Parameter:
    page: Page => Playwright page we need to check, we will check just after clicking the continue, or save buttons
    success_msg: Page => With respect to different pages, there must be different success message we can assign

    Returns:
    child.name: str => name of child
    success: bool => just tell whether success happened or not
    Failure: str => Any pop up messages
    validation_fail: list[str] => fields that are required to fill and not yet filled. If we do regex and we found anything like '.... required', 
    below a field, that is considered validation_fail.
    """

    def __init__(self, page: Page, success_msg: str = "Successfully completed this process"):
        self.page = page
        self.detection_success_msg = success_msg
        

    def _check_duplicate_record(self) -> bool:
        """
        It will check for the children whose duplicate record found error is coming.
        We just need to see that, after clicking button is there anything related to 
        <h3 class="text-xl font-bold text-gray-800">Duplicate Record Found</h3>
        if it is there, we are entering duplicate records, so just close the panal
        """

        duplicate_heading = self.page.get_by_role(
            "heading",
            name="Duplicate Record Found"
        )

        if duplicate_heading.is_visible():
            return True
        return False

        
    def _check_validation_failure(self) -> list[str]:
        """
        It will check after the click that in the page, is there any red line occured or written.
        It will be a simple text, just the change is, in the end, 'required' is written, or something like this is there
        <p class="text-red-500 text-xs mt-1">Facility Name is required</p> there could be any form of text-red-...., so we
        need to think whether to use class as a selector

        Parameters:
        None

        Returns:
        validation_errors: list[str] | None = Maybe more than one string is present, I want to show the user all the string at once, so that 
        they could correct in one go
        """
        IGNORED_MESSAGES = {
            'Health status is set to "Identified" because defects have been detected.'
        }

        VALIDATION_KEYWORDS = {
            "required",
            "invalid",
            "mandatory",
            "please",
            "select",
            "enter",
            "must"
        }
        validation_errors = []

        error_elements = self.page.locator("p[class*='text-red-'], span[class*='text-red-']")

        count = error_elements.count()

        for i in range(count):
            try:
                element = error_elements.nth(i)

                if not element.is_visible():
                    continue

                text = (element.text_content() or "").strip()

                if not text:
                    continue

                if text == "*":
                    continue

                if text in IGNORED_MESSAGES:
                    continue

                if any(
                    keyword in text.lower()
                    for keyword in VALIDATION_KEYWORDS
                ):
                    validation_errors.append(text)

            except Exception as e:
                logging.error(f"Error occured while getting validation error as : {e}")
                continue
        
        return validation_errors
    
    def _is_current_screen_present(self, current_screen_target: Locator) -> bool:
        """
        check whether the target is present or not. Target means there will be an element that will be provided by the 
        user when using the 'check' method, that element or locator we need to check whether it is present or not, like the
        heading of the page, before clicking, to check whether now are we on that page only or not?
        """

        if current_screen_target.is_visible():
            return True
        return False

    def _is_next_screen_present(self,next_screen_target: Locator) -> bool:
        """
        If next screen is present then it is success

        Parameter:
        Next_screen_target: Locator => anything or any heading that must be only in next screen

        Returns:
        success: bool => has success happened
        """

        if next_screen_target.is_visible():
            return True
        return False
    
    def check(self, current_screen_target: Locator, next_screen_target:Locator) -> FeedbackResult:
        """
        Method use to check the state of failure or success by the UI. 
        Parameter:
        target: Locator = A target element that I can check after clicking button if it is present then error occured.
        Next_screen_target: Locator => anything or any heading that must be only in next screen

        Returns:
        FeedbackResult
        """


        ## Step 0: Check for duplicate record
        if self._check_duplicate_record():
            return FeedbackResult(outcome=FeedbackOutcome.DUPLICATE,message="Duplicate of this child is present")
        
        
        ## If next screen is present then success
        success = self._is_next_screen_present(next_screen_target)
        if success:
            return FeedbackResult(outcome=FeedbackOutcome.SUCCESS,message=self.detection_success_msg)

        ## Step 1: Check for validation error, if it happens that validation error 
        validation_err_msg = self._check_validation_failure()
        if len(validation_err_msg) > 0:
            return FeedbackResult(outcome=FeedbackOutcome.VALIDATION_ERROR, message="Some validation related errors happened", validation_errors=validation_err_msg)
        
        
        ## Step 2: First check whether the target/current screen is visible is present or not
        isTargetPresent = self._is_current_screen_present(current_screen_target=current_screen_target)

        if isTargetPresent:
            ## It means error happened, then check for error message 
            return FeedbackResult(outcome=FeedbackOutcome.FAILURE, message="Can't save this child, current screen is present.")
        

        ## If nothing happens from these it means it failed unknowingly
        return FeedbackResult(outcome=FeedbackOutcome.UNKNOWN, message="Unknown error happened, returning to enter new child.")
    

        