import logging

from worker.MetadataProvider import MetadataProvider
from all_models.WorkerContext import WorkerContext
from all_models.JobMetadata import JobMetadata
from all_models.UserMetadata import UserMetadata
from services.JobManager import JobManager

from repository.UserRepository import UserRepository


class DatabaseMetadataProvider(MetadataProvider):

    def get_context(self, userReposity: UserRepository, user_id: str):
        user = userReposity.get_by_userId(user_id=user_id)
        return WorkerContext(userName=user.user_name, password=user.password)
        

        
        
