from dataclasses import dataclass

from constants.log_type import LogType

@dataclass
class JobLog:
    timeStamp: str
    message: str
    type: LogType = LogType.INFO
