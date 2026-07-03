from enum import Enum

class Commands(Enum):
    """
    Each api request for now is considered as Producer. User interacts twice with the server, 
    1. First time it ask for create job, then server will handle opening browser -> login -> institution page, and returns(through websockets) list of institutions
    for that day of screening.
    2. THen user selects one of the institution and send back, that same worker will start with screening and report generation
    NOTE: for version 1, these two will be the commands, no cancel and pause.
    """
    GET_INSTITUTION = "get_institution"
    START_SCREENING = "start_screening"
    GET_USER_METADATA = "get_user_metadata"