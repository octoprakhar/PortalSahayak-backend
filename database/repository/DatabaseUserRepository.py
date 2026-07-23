from repository.UserRepository import UserRepository

from database.Database import Database
from database.model.User import User

class DatabaseUserRepository(UserRepository):

    def __init__(self, database: Database):
        super().__init__()
        self.db = database


    def create(self, user:User) -> str:
        response = (
            self.db.client
            .table("User")
            .insert(
                {
                    "user_name": user.user_name,
                    "password": user.password,
                }
            )
            .execute()
        )

        if not response.data:
            raise Exception("Failed to create user.")

        return response.data[0]["user_id"]
    
    def get_by_userId(self, user_id):
        response = (
            self.db.client
            .table("User")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            return None

        row = response.data[0]

        return User(
            user_id=row["user_id"],
            created_at=row["created_at"],
            user_name=row["user_name"],
            password=row["password"],
            doctor_name=row.get("doctor_name"),
            district_id=row.get("district_id"),
            health_block_id=row.get("health_block_id"),
            state_id=row.get("state_id"),
            mht_code=row.get("mht_code"),
            selected_facility=row.get("selected_facility"),
        )
    
    def get_by_username(self, username):
        response = (
            self.db.client
            .table("User")
            .select("*")
            .eq("user_name", username)
            .execute()
        )

        if not response.data:
            return None

        row = response.data[0]

        return User(
            user_id=row["user_id"],
            created_at=row["created_at"],
            user_name=row["user_name"],
            password=row["password"],
            doctor_name=row.get("doctor_name"),
            district_id=row.get("district_id"),
            health_block_id=row.get("health_block_id"),
            state_id=row.get("state_id"),
            mht_code=row.get("mht_code"),
            selected_facility=row.get("selected_facility"),
        )
    
    def update_registration_metadata(self, user_id, registrationMetadata):
        response = (
            self.db.client
            .table("User")
            .update(
                {
                    "doctor_name": registrationMetadata.user_name,
                    "district_id": registrationMetadata.district_id,
                    "health_block_id": registrationMetadata.health_block_id,
                    "state_id": registrationMetadata.state_id,
                    "mht_code": registrationMetadata.mht_code,
                }
            )
            .eq("user_id", user_id)
            .select()
            .execute()
        )

        if not response.data:
            raise Exception("User not found.")

        return response.data[0]["user_id"]
    
    def update_selected_facility(self, user_id, select_facility):
        response = (
            self.db.client
            .table("User")
            .update(
                {
                    "selected_facility": select_facility,
                }
            )
            .eq("user_id", user_id)
            .select()
            .execute()
        )

        if not response.data:
            raise Exception(f"User with id '{user_id}' not found.")

        return response.data[0]["user_id"]
    
    def remove_user_by_id(self, user_id):
        response = (
            self.db.client
            .table("User")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )

        # If no rows were deleted, response.data will be empty.
        return len(response.data) > 0