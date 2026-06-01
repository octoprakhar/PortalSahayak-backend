from dataclasses import dataclass
from playwright.sync_api import Locator

@dataclass
class SearchResult:
    found: bool
    eligible: bool
    locator: Locator | None = None

@dataclass
class SearchedStudentCandidate:
    name: str
    dob: str
    fatherName: str
    motherName: str
    isChildEligibleForScreening: bool ## Is start editing button present
    locator: Locator