from datetime import datetime, timezone
from fastapi import UploadFile
from io import BytesIO

from database.Database import Database
from database.repository.DatabaseJobRepository import DatabaseJobRepository
from database.model.MetadataForJobCreation import MetadataForJobCreation
from all_models.ClassRange import ClassRange
from constants.job_status import JobStatus
from all_models.InstitutionData import InstitutionData
from constants.institution_type import InstitutionType

def test_create_job():
    db = Database()
    repository = DatabaseJobRepository(db)

    metadata = MetadataForJobCreation(
        user_id="bc575216-5ec3-4fbf-ae34-c3f0092fcb3a",
        status=JobStatus.IDLE,
        address="New York",
        mobile_number="1234567890",
        planned_date=datetime.now(timezone.utc).isoformat(),
        class_range=ClassRange(
            from_class=1,
            to_class=5,
        ),
        is_anm_present=True,
        existing_limit=100,
    )

    job_id = repository.create(metadata)

    assert job_id is not None, "job_id should not be None"
    assert isinstance(job_id, str), f"Expected str, got {type(job_id)}"

    print("✅ Test passed!")
    print(f"Created job ID: {job_id}")


def test_get_job_by_job_id():
    db = Database()
    repository = DatabaseJobRepository(db)

    metadata = MetadataForJobCreation(
        user_id="bc575216-5ec3-4fbf-ae34-c3f0092fcb3a",
        status=JobStatus.IDLE,
        address="New York",
        mobile_number="1234567890",
        planned_date=datetime.now(timezone.utc).isoformat(),
        class_range=ClassRange(
            from_class=1,
            to_class=5,
        ),
        is_anm_present=True,
        existing_limit=100,
    )

    job_id = repository.create(metadata)

    job = repository.get_job_by_job_id(job_id)

    assert job.job_id == job_id
    assert job.user_id == metadata.user_id
    assert job.status == metadata.status
    assert job.address == metadata.address
    assert job.mobile_number == metadata.mobile_number
    assert job.planned_date == metadata.planned_date
    assert job.is_anm_present == metadata.is_anm_present
    assert job.existing_limit == metadata.existing_limit

    assert job.class_range.from_class == metadata.class_range.from_class
    assert job.class_range.to_class == metadata.class_range.to_class

    print("✅ Test passed!")
    print(job)

def test_upload_institution_data():
    db = Database()
    repository = DatabaseJobRepository(db)

    metadata = MetadataForJobCreation(
        user_id="bc575216-5ec3-4fbf-ae34-c3f0092fcb3a",
        status=JobStatus.IDLE,
        address="New York",
        mobile_number="1234567890",
        planned_date=datetime.now(timezone.utc).isoformat(),
        class_range=ClassRange(1, 5),
        is_anm_present=True,
        existing_limit=100,
    )

    job_id = repository.create(metadata)

    institution = InstitutionData(
        institution_plan_id=123,
        institution_name="Government School",
        institution_type=InstitutionType.SCHOOL,
        planned_date=datetime.now(timezone.utc).isoformat(),
    )

    repository.upload_institution_data(job_id, institution)

    job = repository.get_job_by_job_id(job_id)

    assert job.institution_data is not None

    assert (
        job.institution_data.institution_plan_id
        == institution.institution_plan_id
    )

    assert (
        job.institution_data.institution_name
        == institution.institution_name
    )

    assert (
        job.institution_data.institution_type
        == institution.institution_type
    )

    assert (
        job.institution_data.planned_date
        == institution.planned_date
    )

    print("✅ Test passed!")

def test_upload_file():

    db = Database()
    repository = DatabaseJobRepository(db)

    # First create a job
    metadata = MetadataForJobCreation(
        user_id="bc575216-5ec3-4fbf-ae34-c3f0092fcb3a",
        status=JobStatus.IDLE,
        address="New York",
        mobile_number="1234567890",
        planned_date=datetime.now(timezone.utc).isoformat(),
        class_range=ClassRange(
            from_class=1,
            to_class=5,
        ),
        is_anm_present=True,
        existing_limit=100,
    )

    job_id = repository.create(metadata)


    # Create fake uploaded file
    file_content = b"Hello, this is a test file"

    upload_file = UploadFile(
        filename="test.txt",
        file=BytesIO(file_content),
    )


    # Upload file
    file_path = repository.upload_file(
        job_id=job_id,
        file=upload_file,
    )


    # Verify storage path
    assert file_path is not None
    assert isinstance(file_path, str)

    assert job_id in file_path
    assert "test.txt" in file_path


    # Verify database was updated
    job = repository.get_job_by_job_id(job_id)

    assert job.upload_file_path is not None
    assert job.upload_file_path == file_path


    print("✅ Test passed!")
    print(f"Uploaded file path: {file_path}")


if __name__ == "__main__":
    # test_create_job()
    # test_get_job_by_job_id()
    # test_upload_institution_data()
    test_upload_file()