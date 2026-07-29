from abc import ABC, abstractmethod

from all_models.WorkerContext import WorkerContext
from repository.UserRepository import UserRepository


class MetadataProvider(ABC):
    """
    This family of classes will help to provider context/metadata 
    to the workers before they wanna run, if they provide from local 
    file, it is different class, or through db, or cloud, etc.

    The primary goal of the metadata/worker, is to tell the background of the user for which we are doing the work.
    I mean for which user and for which job
    """

    @abstractmethod
    def get_context(self,userRepository: UserRepository) -> WorkerContext:
        """
        This method will be used to give context to the worker by taking 
        the job_id in which it is working. and user_id, the id of the user
        """
        pass