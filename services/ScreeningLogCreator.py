from pathlib import Path
import json
from datetime import datetime

from constants.log_type import LogType

class ScreeningLogCreator:
    """
    Creates and manages temporary screening logs.

    Logs are stored at:
        tmp/<job_id>/logs/log.json

    These logs can later be uploaded to the database.
    """

    def __init__(self, job_id: str):
        self.job_id = job_id

        self.log_dir = Path("tmp") / job_id / "logs"
        self.log_file = self.log_dir / "log.json"

        # Create directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create empty log file if it doesn't exist
        if not self.log_file.exists():
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def append_log(self, log_type: LogType, message: str):
        """
        Append a log entry.

        Args:
            log_type: LogType enum
            message: Log message
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": log_type.value,
            "message": message,
        }

        with open(self.log_file, "r+") as f:
            logs = json.load(f)
            logs.append(entry)

            f.seek(0)
            json.dump(logs, f, indent=4)
            f.truncate()

    def flush(self) -> str:
        return str(self.log_file)