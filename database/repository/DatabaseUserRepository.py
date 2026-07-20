from repository.UserRepository import UserRepository

class DatabaseUserRepository(UserRepository):

    def create(self, user):
        pass
    
    def get_by_userId(self, user_id):
        pass
    
    def get_by_username(self, username):
        pass
    
    def update_registration_metadata(self, user_id, registrationMetadata):
        pass
    
    def update_selected_facility(self, user_id, select_facility):
        pass
    
    def remove_user_by_id(self, user_id):
        pass