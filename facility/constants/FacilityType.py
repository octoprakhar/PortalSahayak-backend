from enum import Enum

class FacilityType(str, Enum):
    BLOCK = "Block Level Facility"
    DISTRICT = "District Level Facility"
    NRC = "NRC"
    DEIC = "DEIC"