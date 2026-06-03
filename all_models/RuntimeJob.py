from dataclasses import dataclass

@dataclass
class RuntimeJob:
    playwright: object
    browser: object
    context: object
    page: object