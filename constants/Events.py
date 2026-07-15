from enum import Enum

class Events(Enum):
    """
    Events will not be directly given to the user. It will help in updating the state of the job, and also it will be sent to the 
    Websocket server, and it will decide which message is required to send back to the user.
    Diferent events are:
    1. WORKER_STARTED : It will be triggered when browser will get fired and that website's /login page opens.
    2. LOGIN_COMPLETED:  It will be fired when we had completed the login of the user, using the username and password they had provided
    3. INSTITUTION_FETCHED: It will be triggered when we entered the institution page, and get the list of institutions of that screening date
    user provides.
    4. INSTITUTION_SELECTED: It will be triggered when user has sent the selected institution back to us.
    5. JOB_FAILED: If any error occured, and we can't move forward.
    6. REPORT_CREATED: When all children entries are done and we have created all the report, success_report, and failure_report of students
    with all the data columns we needed.
    7. LOG_MESSAGE: It is the event that will be thrown when new log message must needed to get written.
    8. REGISTRATION_METADATA_FETCHED: When we fetch the metadata after user has send us the detail
    9. USER_AUTHENTICATION_FAILED: Credentials given by user is wrong
    10. FACILITY_CATALOG_FETCHED: Facility related to a user is fetched and catalog is ready.
    11. FETCHING_FACILITY_FAILED: Error occured while fetching the facility
    12. FETCHING_USER_CREDENTIALS_FAILED : Error while getting session's data like accessToken etc

    NOTE: For v1, JOB_CREATED,LOGIN_COMPLETED,INSTITUTION_FETCHED: is considered the state with api call to 'create-job', and the 'REPORT_CREATED'
    will be for api request 'start-screening'.
    """
    WORKER_STARTED = "worker_started"
    LOGIN_COMPLETED = "login_completed"
    INSTITUTION_FETCHED = "institution_fetched"
    INSTITUTION_SELECTED = "institution_selected"
    REGISTRATION_METADATA_FETCHED = "registration_metadata_fetched"
    USER_AUTHENTICATION_FAILED = "user_authentication_failed"
    JOB_FAILED = "job_failed"
    REPORT_CREATED= "report_created"
    LOG_MESSAGE="log_message"
    FACILITY_CATALOG_FETCHED = "facility_catalog_fetched"
    FETCHING_FACILITY_FAILED = "fetching_facility_failed"
    FETCHING_USER_CREDENTIALS_FAILED = "fetching_user_credentials_failed"