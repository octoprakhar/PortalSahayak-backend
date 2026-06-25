from enum import Enum

class ChildType(Enum):
    """
    There are 3 types of child that will get return during the screening process.
    Child type means different types of ways we are entering child they are NEW_CHILD, EXISTING_CHILD, EXISTING_CHILD_WITHOUT_DATA
    """
    NEW_CHILD = "new_child"
    EXISTING_CHILD = "existing_child"
    EXISTING_CHILD_WITHOUT_DATA = "existing_child_without_data"