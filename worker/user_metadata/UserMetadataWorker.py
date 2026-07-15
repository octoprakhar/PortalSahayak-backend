from playwright.sync_api import Page,BrowserContext,Browser,Playwright

from worker.WorkerAbstract import WorkerAbstract
from all_models.Message import Message
from constants.WorkerState import WorkerState

from constants.Commands import Commands
from all_models.UserRegistrationMetadata import UserRegistrationMetadata
from all_models.PortalCredentials import PortalCredentials
from services.RuntimeManager import RunTimeManager
from constants.Events import Events

class UserMetadataWorker(WorkerAbstract):
    """
    This worker will handle the worklow when user sends userName and password for registration, it will 
    collect the metadata of user, by login in and getting 
    """
    def __init__(self, job_id, worker_context):
        super().__init__(job_id, worker_context)
        self.page: Page = None
        self.browser: Browser = None
        self.browswer_context: BrowserContext = None
        self.playwright: Playwright = None

    def _get_cookie_value(self, name: str) -> str | None:
        return next(
            (
                cookie["value"]
                for cookie in self.browswer_context.cookies()
                if cookie["name"] == name
            ),
            None,
        )

    def _handle_get_user_metadata(self,message:Message):
        runtimeManager = RunTimeManager(job_id=self.job_id, logger=self.log)

        runtime_job = runtimeManager.launch_browser_instance()

        self.page = runtime_job.page
        self.browser = runtime_job.browser
        self.browswer_context = runtime_job.context
        self.playwright = runtime_job.playwright
        

        userName = self.worker_context.userName
        password = self.worker_context.password
        result = runtimeManager.get_user_registration_metadata(page=self.page, userName=userName, password=password)
        # print(f"Got results as \n{result}")

        if result["status_Code"] == '401' or result['status_Code'] == '423':
            self._emit_event(event=Events.USER_AUTHENTICATION_FAILED)
            return
        
        # print("calling to get access tokens")
        access_token = self._get_cookie_value(name="accessToken")
        # print(f"Got access Token as: {access_token}")
        if not access_token:
            self._emit_event(event=Events.FETCHING_USER_CREDENTIALS_FAILED)
            return
        
        portalCredentials = PortalCredentials(acecss_token=access_token)
        # print(f"Made portal credentials as : {portalCredentials}")

        user = result["data"]["user"]
        registrationMetadata = UserRegistrationMetadata(user_name=user["userName"],district_id=user["district_ID"], health_block_id=user["healthBlock_ID"],state_id=user["state_ID"],mht_code=user["mhT_Code"])
        self._emit_event(event=Events.REGISTRATION_METADATA_FETCHED, payload={"registrationMetadata":registrationMetadata, "portalCredentials": portalCredentials})
                

    def _process_command(self, message:Message):
        if message.command == Commands.GET_USER_METADATA:
            print("got command to start metadata worker")
            self._handle_get_user_metadata(message=message)

    
    def shutdown(self):
        self.running = False
        self.worker_state = WorkerState.STOPPED

        if self.page:
            self.page.close()
        if self.browswer_context:
            self.browswer_context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()