from dataclasses import dataclass

@dataclass
class FacilityCatalog:
    facilities_by_type: dict[str,list[str]]
    created_at: str