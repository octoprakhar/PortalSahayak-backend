from abc import ABC,abstractmethod
from typing import Dict

from database.model.User import User
from all_models.UserRegistrationMetadata import UserRegistrationMetadata

class UserRepository(ABC):
    """
    This class will help do the user related CRUD operations out there.
    """

    @abstractmethod
    def create(self, user: User) -> str:
        """
        It creates user and returns the userId
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User:
        """
        It returns the whole user by userName
        """
        pass

    @abstractmethod
    def get_by_userId(self, user_id: str) -> User:
        """
        Get full data of the user using userId
        """
        pass

    @abstractmethod
    def update_registration_metadata(self,user_id: str, registrationMetadata: UserRegistrationMetadata) -> str:
        """
        Update the userId from registration metadata, and returns user_id
        """
        pass

    @abstractmethod
    def update_selected_facility(self,user_id: str, select_facility: Dict[str,str]) -> str:
        """
        Update user facility preference. And return the user id
        """

    @abstractmethod
    def update_full_facility_catalog(self, user_id: str, full_facility_catalog: Dict[str,str]) -> str:
        """
        All the facilities type with name, and fetched date as json data to save
        """

    @abstractmethod
    def remove_user_by_id(self,user_id: str)-> bool:
        """
        Removes the user with id. And then return the boolean whether removes the True/False.
        """
        pass