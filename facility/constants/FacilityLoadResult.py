from enum import Enum

class FacilityLoadResult(Enum):
    SERVER = "server"
    CACHE = "cache"
    EMPTY = "empty"