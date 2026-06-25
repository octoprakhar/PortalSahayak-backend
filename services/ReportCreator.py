from all_models.ChildRunResult import ChildRunResult
from services.JobManager import JobManager


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

    def flush(self)-> tuple[str,str]:
        """
        It will give out two csv or excel any file, when event listner calls it, for that id.
        """

        ## Create both the csv files for now.

        success_path, failure_path = JobManager.save_success_and_failure_files(job_id=self.job_id,success_rows=self.success_results,failure_rows=self.failure_results)
        return success_path,failure_path
