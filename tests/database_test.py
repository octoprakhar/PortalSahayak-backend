from database.Database import Database
from database.model.User import User
from database.repository.DatabaseUserRepository import (
    DatabaseUserRepository,
)

from all_models.UserRegistrationMetadata import UserRegistrationMetadata


def test_create_user():

    database = Database()

    repository = DatabaseUserRepository(
        database=database
    )

    user = User(
        user_name="test_user_123",
        password="test_password",
    )

    user_id = repository.create(user)

    assert user_id is not None

    print(f"Created user: {user_id}")

# test_create_user()

## Get user by id

database = Database()

repository = DatabaseUserRepository(
    database=database
)
# user = repository.get_by_userId("2d1b1ce0-459e-4052-beff-46240554fd2f")

# user = repository.get_by_username("test_user_123")

# if user is None:
#     print("User not found")
# else:
#     print(user)
#     print(user.user_name)


## Updating user

def test_update_registration_metadata():
    database = Database()
    repository = DatabaseUserRepository(database)

    # First create a user
    user_id = repository.create(
        User(
            user_name="test_user",
            password="password123",
        )
    )

    metadata = UserRegistrationMetadata(
        user_name="Dr. John Doe",
        district_id=12,
        health_block_id=5,
        state_id=1,
        mht_code=12345,
    )

    updated_user_id = repository.update_registration_metadata(
        user_id,
        metadata,
    )

    assert updated_user_id == user_id

    user = repository.get_by_userId(user_id)

    assert user.doctor_name == "Dr. John Doe"
    assert user.district_id == 12
    assert user.health_block_id == 5
    assert user.state_id == 1
    assert user.mht_code == 12345

    print("Registration metadata updated successfully!")

# test_update_registration_metadata()

## Now select facility test
def test_update_selected_facility():
    database = Database()

    repository = DatabaseUserRepository(database)

    # Create a test user
    user = User(
        user_name="facility_test_user",
        password="password123",
    )

    user_id = repository.create(user)

    selected_facility = {
        "facility_id": "FAC001",
        "facility_name": "District Hospital",
        "facility_type": "Hospital",
    }

    updated_user_id = repository.update_selected_facility(
        user_id,
        selected_facility,
    )

    assert updated_user_id == user_id

    updated_user = repository.get_by_userId(user_id)

    assert updated_user is not None
    assert updated_user.selected_facility == selected_facility

    print("Selected facility updated successfully!")
    print(updated_user.selected_facility)


def test_remove_user():
    database = Database()
    repository = DatabaseUserRepository(database=database)

    # Create a user first
    user = User(
        user_name="delete_test_user",
        password="password123",
    )

    user_id = repository.create(user)

    # Delete the user
    success = repository.remove_user_by_id(user_id)

    assert success

    # Verify the user is gone
    deleted_user = repository.get_by_userId(user_id)

    assert deleted_user is None

    print(f"Successfully deleted user: {user_id}")


if __name__ == "__main__":
    # test_update_selected_facility()
    test_remove_user()