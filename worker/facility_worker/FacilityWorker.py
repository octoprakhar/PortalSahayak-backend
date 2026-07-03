from zoneinfo import ZoneInfo
from datetime import datetime
import requests
from dataclasses import asdict

from worker.WorkerAbstract import WorkerAbstract

from all_models.Message import Message
from constants.Commands import Commands
from constants.Events import Events
from all_models.FacilityCatalog import FacilityCatalog
from all_models.WorkerContext import WorkerContext

## dto models
from all_models.dto.request.FacilityTypeRequest import FacilityTypeRequest
from all_models.dto.request.FacilityNameRequest import FacilityNameRequest
from all_models.dto.response.FacilityTypeResponse import FacilityTypeResponse, FacilityData

class FacilityWorker(WorkerAbstract):
    """
    This workers sole purpose is to first it get facility Type and then 
    for each facility type it gets facility name using user registration metadata
    """
    def __init__(self, job_id, worker_context:WorkerContext):
        super().__init__(job_id, worker_context)
        self.facility_fetching_url = "https://rbsk.mohfw.gov.in/rbsk_webapi/api/Hierarchy_Master/Get_HierarchyMaster"
        self.masterType_for_fetching_facility_type = 10
        self.masterType_for_fetching_facility_names = 11

    def _has_required_facilities(
        self,
        facilities_by_type: dict[str, list[str]]
    ) -> bool:
        """
        Required:
        - Block Level Facility
        - NRC
        - Either DEIC or District Level Facility

        Each required type must have at least one facility.
        """

        has_block = bool(facilities_by_type.get("Block Level Facility"))
        has_nrc = bool(facilities_by_type.get("NRC"))
        has_deic = bool(facilities_by_type.get("DEIC"))
        has_district = bool(facilities_by_type.get("District Level Facility"))

        return has_block and has_nrc and (has_deic or has_district)

    def _fetch_all_facility_type(self) -> list[FacilityData]:
        # print('Fetching facility types')
        request_body = FacilityTypeRequest(masterType=self.masterType_for_fetching_facility_type, stateID=self.worker_context.user_registration_metadata.state_id)
        response = requests.post(self.facility_fetching_url, json=asdict(request_body), verify=False)


        if response.status_code != 200:
            # print("Failed to get response")
            return []
        
        response_data = response.json()
        # Convert each item in the data list
        facility_list = [
            FacilityData(**item)
            for item in response_data["data"]
        ]

        return facility_list
        
        

    def _fetch_facilities_by_type(self,facility_type: FacilityData) -> list[str]:
        """
        Just return the names list of each facility type
        """
        request_body = FacilityNameRequest(masterType=self.masterType_for_fetching_facility_names, stateID=self.worker_context.user_registration_metadata.state_id, districtID=self.worker_context.user_registration_metadata.district_id, healthBlockID=self.worker_context.user_registration_metadata.health_block_id, mhtid=self.worker_context.user_registration_metadata.mht_code, facilityType=facility_type.code)

        response = requests.post(url=self.facility_fetching_url,json=asdict(request_body),verify=False)

        if response.status_code != 200:
            return []
        response_data = response.json()
        if not response_data["data"]:
            return []
        
        # print("-------------------------")
        # print(f"got response data for facility type : {facility_type.name} as: \n{response_data}")

        return [item["name"] for item in response_data["data"]]


    def _handle_catalog_creation(self,message:Message):
        # print("handle facility is called")
        facilities_by_type = {}
        all_facility_types = self._fetch_all_facility_type()
        # print(f"Got facility list as : {all_facility_types}")
        if not all_facility_types or len(all_facility_types) == 0:
            self._emit_event(event=Events.FETCHING_FACILITY_FAILED)
            return
   
        for facility_type in all_facility_types:
            all_facilities_of_a_type = self._fetch_facilities_by_type(facility_type=facility_type)
            facilities_by_type[facility_type.name] = all_facilities_of_a_type

        if not self._has_required_facilities(facilities_by_type):
            # print("Required facilities are missing.")
            self._emit_event(event=Events.FETCHING_FACILITY_FAILED)
            return

        created_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()

        facility_catalog = FacilityCatalog(
            facilities_by_type=facilities_by_type,
            created_at=created_at
        )

        # print(f"Got facility Catalog as: {facility_catalog}")

        self._emit_event(
            event=Events.FACILITY_CATALOG_FETCHED,
            payload={"facility_catalog": facility_catalog}
        )

    
    def _process_command(self, message: Message):
        if message.command == Commands.START_FACILITY_DISCOVERY:
            self._handle_catalog_creation(message=message)
    
    def shutdown(self):
        return super().shutdown()