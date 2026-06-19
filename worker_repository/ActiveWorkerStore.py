import logging

from worker.Worker import Worker

from all_models.WorkerContext import WorkerContext


class ActiveWorkerStore:
    """
    This class is the repository for each worker ever present, 
    It will create new worker
    We can get that worker with that help of job id.
    And also we can delete the worker in the repository
    """

    ## For now in-memory workers will be there dict of [job_id: Worker]
    active_workers: dict[str,Worker] = {}

    @classmethod
    def create_worker(cls, job_id: str, worker_context: WorkerContext) -> Worker:
        """
        It just creates the new worker

        Returns:
        worker: Worker = Worker instance of the current worker, so that it can call and send message to it's mailbox
        """
        try: 
            worker_instance = Worker(job_id=job_id, worker_context=worker_context)
            cls.active_workers[job_id] = worker_instance

            return worker_instance

        except Exception as e:
            logging.exception("ActiveWorkerStore: Error occured while creating worker")
            raise
        
    @classmethod
    def get_worker(cls,job_id: str) -> Worker:
        """
        It is used when worker is already created, and we have job id, and we can get the worker now
        """
        return cls.active_workers[job_id]
    
    @classmethod
    def remove_worker(cls, job_id: str):
        """
        It will destroy the worker
        """
        worker = cls.get_worker(job_id=job_id)
        ## TODO : Step 1: Call workers close browser function to close the page instance, and also if there is the thread then remove it

        ## Step 2: Remove worker from the repository
        del cls.active_workers[job_id]
