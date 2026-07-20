from dataclasses import dataclass
from playwright.sync_api import Locator

@dataclass
class ExistingChildResult:
    name: str
    dob: str
    fatherName: str
    motherName: str
    gender: str
    isStartScreeningButtonPresent: bool
    child_class: int | None