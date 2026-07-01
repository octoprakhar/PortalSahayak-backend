from worker.WorkerAbstract import WorkerAbstract

from constants.WorkerType import WorkerType



class ActiveWorkerStore:
    """
    This class is the repository for each worker ever present, 
    It will create new worker
    We can get that worker with that help of job id.
    And also we can delete the worker in the repository

    My worker will have like this jobId: [workerType]
    """

    ## For now in-memory workers will be there dict of [job_id: {workerType, WorkerAbstract}]
    active_workers: dict[str, dict[WorkerType, WorkerAbstract]] = {}


    @classmethod
    def register_worker(
        cls,
        job_id: str,
        worker_type: WorkerType,
        worker: WorkerAbstract,
    ) -> WorkerAbstract:

        cls.active_workers.setdefault(job_id, {})
        cls.active_workers[job_id][worker_type] = worker

        return worker
    
    @classmethod
    def get_worker(cls,job_id: str, worker_type: WorkerType) -> WorkerAbstract:
        """
        It is used when worker is already created, and we have job id, and we can get the worker now
        """
        return cls.active_workers[job_id][worker_type]
    
    @classmethod
    def has_worker(
        cls,
        job_id: str,
        worker_type: WorkerType,
    ) -> bool:
        """
        Check if a worker exists.
        """
        return (
            job_id in cls.active_workers
            and worker_type in cls.active_workers[job_id]
        )
    
    @classmethod
    def remove_worker(cls, job_id: str, worker_type: WorkerType):
        """
        It will destroy the worker
        """
        worker = cls.get_worker(job_id=job_id,worker_type=worker_type)
        ## TODO : Step 1: Call workers close browser function to close the page instance, and also if there is the thread then remove it

        ## Step 2: Remove worker from the repository
        del cls.active_workers[job_id][worker_type]

        # Remove the job entry if no workers remain.
        if not cls.active_workers[job_id]:
            del cls.active_workers[job_id]
    
    @classmethod
    def remove_all_workers(cls, job_id: str):
        workers = cls.active_workers.get(job_id)

        if not workers:
            return

        # Copy the keys because remove_worker() modifies the dict.
        for worker_type in list(workers.keys()):
            cls.remove_worker(job_id, worker_type)

    @classmethod
    def get_all_workers(
        cls,
        job_id: str,
    ) -> dict[WorkerType, WorkerAbstract]:
        """
        Get all workers for a job.
        """
        return cls.active_workers.get(job_id, {})
