from dataclasses import dataclass

from facility.constants.FacilityType import FacilityType

@dataclass
class ReferralDecision:

    disease_name: str

    facility_type: FacilityType

    facility_name: str