from repository.ReportRepository import ReportRepository

from database.Database import Database
from database.model.JobReport import JobReport
from all_models.ReportFiles import ReportFiles

from database.storage.Storage import Storage

class DatabaseReportRepository(ReportRepository):

    def __init__(self, database: Database):
        super().__init__()
        self.db = database
        self.storage = Storage(client=database.client)

    def create(self,job_report:JobReport, local_temp_file: ReportFiles) -> str:

        ## Upload both the files
        success_file_remote_path = self.storage.upload(bucket_name="screening-data", local_file=local_temp_file.success_report_path,remote_path=job_report.success_file_remote_path)
        failure_file_remote_path = self.storage.upload(bucket_name="screening-data", local_file=local_temp_file.failure_report_path,remote_path=job_report.failure_file_remote_path)
        response = (
            self.db.client
            .table("Job_Report")
            .insert(
                {
                    "user_id": job_report.user_id,
                    "job_id": job_report.job_id,
                    "success_report_path": success_file_remote_path,
                    "failure_report_path": failure_file_remote_path,
                }
            )
            .execute()
        )
        
        if not response.data:
            raise Exception("Failed to create report row.")
        
        return response.data[0]["report_id"]

    def update_log_path(self, report_id: str, local_log_file, remote_path):
         # Upload the log file
        uploaded_path = self.storage.upload(
            bucket_name="screening-data",
            local_file=local_log_file,
            remote_path=remote_path,
        )

        # Update the database
        response = (
            self.db.client
            .table("Job_Report")
            .update({"job_log_path": uploaded_path})
            .eq("report_id", report_id)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to update job log path.")

        return uploaded_path