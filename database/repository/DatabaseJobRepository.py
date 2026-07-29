from fastapi import UploadFile
from postgrest.exceptions import APIError
import uuid


from repository.JobRepository import JobRepository

from database.Database import Database
from database.model.Job import Job

from all_models.InstitutionData import InstitutionData
from database.model.MetadataForJobCreation import MetadataForJobCreation
from constants.job_status import JobStatus
from constants.institution_type import InstitutionType
from all_models.ClassRange import ClassRange

class DatabaseJobRepository(JobRepository):

    def __init__(self, database: Database):
        super().__init__()
        self.db = database

    def create(self, job_creation_metadata: MetadataForJobCreation) -> str:
        payload = {
            "user_id": job_creation_metadata.user_id,
            "job_status": job_creation_metadata.status.value,
            "address": job_creation_metadata.address,
            "mobile_number": job_creation_metadata.mobile_number,
            "planned_date": job_creation_metadata.planned_date,
            "class_range": {
                "from_class": job_creation_metadata.class_range.from_class,
                "to_class": job_creation_metadata.class_range.to_class,
            },
            "is_anm_present": job_creation_metadata.is_anm_present,
            "existing_limit": job_creation_metadata.existing_limit,
        }

        try:
            response = (
                self.db.client
                .table("Screening_Job")
                .insert(payload)
                .execute()
            )

            if not response.data:
                raise RuntimeError("Failed to create job.")

            return response.data[0]["id"]

        except Exception as e:
            raise RuntimeError(f"Unable to create job: {e}") from e

    def upload_institution_data(self,job_id: str, institution_data: InstitutionData) -> str:
        payload = {
            "institution_data": {
                "institution_plan_id": institution_data.institution_plan_id,
                "institution_name": institution_data.institution_name,
                "institution_type": institution_data.institution_type.value,
                "planned_date": institution_data.planned_date,
            }
        }

        try:
            response = (
                self.db.client
                .table("Screening_Job")
                .update(payload)
                .eq("id", job_id)
                .execute()
            )

            if not response.data:
                raise ValueError(f"Job with id '{job_id}' not found.")

            return job_id

        except APIError as e:
            raise RuntimeError(f"Failed to upload institution data: {e}") from e

    def upload_file(self, job_id: str, file: UploadFile) -> str:

        if file.filename is None:
            raise ValueError("Uploaded file does not have a filename.")

        storage_path = f"{job_id}/upload.csv"

        try:
            file_bytes = file.file.read()

            (
                self.db.client
                .storage
                .from_("screening-data")
                .upload(
                    path=storage_path,
                    file=file_bytes,
                    file_options={
                        "content-type": file.content_type or "application/octet-stream"
                    },
                )
            )

            response = (
                self.db.client
                .table("Screening_Job")
                .update(
                    {
                        "upload_file_path": storage_path
                    }
                )
                .eq("id", job_id)
                .execute()
            )

            if not response.data:
                raise ValueError(f"Job with id '{job_id}' not found.")

            return storage_path

        except Exception as e:
            raise RuntimeError(f"Failed to upload file: {e}") from e

        
    def get_job_by_job_id(self, job_id: str) -> Job:
        response = (
            self.db.client
            .table("Screening_Job")
            .select("*")
            .eq("id", job_id)
            .execute()
        )

        if not response.data:
            raise ValueError(f"Job with id '{job_id}' not found.")

        row = response.data[0]

        institution = None

        if row["institution_data"] is not None:
            institution = InstitutionData(
                institution_plan_id=row["institution_data"]["institution_plan_id"],
                institution_name=row["institution_data"]["institution_name"],
                institution_type=InstitutionType(
                    row["institution_data"]["institution_type"]
                ),
                planned_date=row["institution_data"]["planned_date"],
            )

        return Job(
            job_id=row["id"],
            user_id=row["user_id"],
            status=JobStatus(row["job_status"]),
            created_at=row["created_at"],
            address=row["address"],
            mobile_number=row["mobile_number"],
            planned_date=row["planned_date"],
            class_range=ClassRange(
                from_class=row["class_range"]["from_class"],
                to_class=row["class_range"]["to_class"],
            ),
            is_anm_present=row["is_anm_present"],
            existing_limit=row["existing_limit"],
            upload_file_path=row["upload_file_path"],
            institution_data=institution
        )

    def get_uploaded_file_url(self, job_id, file_path) -> str | None:
        if not file_path:
            return None
        public_url = (
            self.db.client.storage
            .from_("screening-data")
            .get_public_url(file_path)
        )
        return public_url

    def update_job_status(self, job_id, new_status):
        payload = {
            "job_status": new_status.value
        }

        try:
            response = (
                self.db.client
                .table("Screening_Job")
                .update(payload)
                .eq("id", job_id)
                .execute()
            )

            if not response.data:
                raise ValueError(f"Job with id '{job_id}' not found.")

            return job_id

        except APIError as e:
            raise RuntimeError(f"Failed to update job status: {e}") from e