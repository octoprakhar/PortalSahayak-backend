from abc import ABC, abstractmethod

from all_models.WorkerContext import WorkerContext

class MetadataProvider(ABC):
    """
    This family of classes will help to provider context/metadata 
    to the workers before they wanna run, if they provide from local 
    file, it is different class, or through db, or cloud, etc.

    The main goal of this class's family is to remove the direct dependency of 
    a worker in calling persistance data sources. Worker is responsible for runtime 
    management like playwright, page etc, not the database. So they will provide data
    to the worker, at the time of making of worker.
    """

    @abstractmethod
    def get_context(self,job_id: str) -> WorkerContext:
        """
        This method will be used to give context to the worker by taking 
        the job_id in which it is working.
        """
        pass