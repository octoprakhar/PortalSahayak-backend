from dataclasses import dataclass

@dataclass
class FacilityData:
    code: int
    name: str


@dataclass
class FacilityTypeResponse:
    succecced:bool
    message:str
    status_Code: int | None
    errors: str | None
    data: list[FacilityData]


