from abc import ABC,abstractmethod

from database.model.JobReport import JobReport
from all_models.ReportFiles import ReportFiles

class ReportRepository(ABC):
    """
    After completion, this repository will help in creating the final reports 
    """

    @abstractmethod
    def create(self,job_report: JobReport, local_temp_file: ReportFiles)-> str:
        """
        It will create the report row, with success and falure files path, and returns report_id
        """
        pass

    @abstractmethod
    def update_log_path(self, report_id: str, local_log_file: str, remote_path: str) -> str:
        """
        It will update the log file path for the specific row
        """
        pass
