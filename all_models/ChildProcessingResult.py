from dataclasses import dataclass

@dataclass
class ChildProcessingResult:
    child_name: str
    father_name: str
    outcome: str
    message: str