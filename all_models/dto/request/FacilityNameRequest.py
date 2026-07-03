from dataclasses import dataclass

@dataclass
class FacilityNameRequest:
    masterType: int
    stateID: int
    districtID: int
    healthBlockID: int
    mhtid: int
    facilityType: int