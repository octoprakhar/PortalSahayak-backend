from pathlib import Path
import csv

from all_models.ChildRunResult import ChildRunResult
from all_models.ReportFiles import ReportFiles
from utils.persistantUtils import to_report_row


class ReportCreator:
    """
    This Method will help in creating final screening report(for now, in future maybe preprocessing report too),
    for both failure and success.
    For specific job there will be a report creator, maybe we need for each job a report creator, or at time of making worker, we could pass one.
    """

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.failure_results: list[ChildRunResult] = []
        self.success_results: list[ChildRunResult] = []
        self.REPORT_COLUMNS = [
            "Name",
            "DOB",
            "Father Name",
            "Mother Name",
            "Mobile",
            "Gender",
            "Address",
            "Child Type",
            "Original Height",
            "Final Height",
            "Original Weight",
            "Final Weight",
            "Original HB",
            "Final HB",
            "Original Head Circumference",
            "Final Head Circumference",
            "Original Disease",
            "Final Disease",
            "Stage",
            "Status",
            "Message",
            "Validation Errors",
        ]

    def add_success(self,child_result: ChildRunResult)-> None:
        """
        It will get Child's final success result, convert it in PortalSuccessRow, and save it.
        """
        self.success_results.append(child_result)
    
    def add_failure(self,child_result: ChildRunResult)-> None:
        """
        It will get child's failure either in personal detail, or in health saving, if failure , convert it in PortalFailureRow, and save it
        """
        self.failure_results.append(child_result)

    def _write_csv(self,path: Path, results: list[ChildRunResult]) -> None:
        """
        THis will help in writing ChildRunResult in csv
        """

        rows = [to_report_row(result=result) for result in results]

        ## If there are not rows, we will still create file with headers
        with path.open("w",newline="",encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=self.REPORT_COLUMNS)
            writer.writeheader()

            if rows:
                writer.writerows(rows)

    def flush(self)-> ReportFiles:
        """
        Creates:
            root/
                tmp/
                    <job_id>/
                        success.csv
                        failure.csv
        """

        # Project root = directory where this file lives 
        project_root = Path(__file__).resolve().parent.parent

        report_dir = project_root / "tmp" / self.job_id / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        success_path = report_dir / "success.csv"
        failure_path = report_dir / "failure.csv"

        self._write_csv(success_path, self.success_results)
        self._write_csv(failure_path, self.failure_results)

        return ReportFiles(
            success_report_path=str(success_path),
            failure_report_path=str(failure_path),
        )

