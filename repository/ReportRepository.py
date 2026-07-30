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