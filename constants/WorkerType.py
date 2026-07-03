from enum import Enum

class WorkerType(Enum):
    """
    Different types of worker doing different things 
    """
    INSTITUTION_DATA_WORKER= "institution_data_worker"
    SCREENING_WORKER = "screening_worker"
    USER_METADATA_WORKER = "user_metadata_worker"
    FACILITY_WORKER = "facility_worker"