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
from all_models.UserRegistrationMetadata import UserRegistrationMetadata
## dto models
from all_models.dto.request.FacilityTypeRequest import FacilityTypeRequest
from all_models.dto.request.FacilityNameRequest import FacilityNameRequest
from all_models.dto.response.FacilityTypeResponse import FacilityTypeResponse, FacilityData
from all_models.PortalCredentials import PortalCredentials



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

    def _make_headers(self,credentials: PortalCredentials):
        return {
        "Cookie": f"accessToken={credentials.acecss_token}"
        }

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

    def _fetch_all_facility_type(self, stateId: int, portalCredentials: PortalCredentials) -> list[FacilityData]:
        # print('Fetching facility types')
        request_body = FacilityTypeRequest(masterType=self.masterType_for_fetching_facility_type, stateID=stateId)
        response = requests.post(self.facility_fetching_url, json=asdict(request_body), verify=False,headers=self._make_headers(credentials=portalCredentials))


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
        
        

    def _fetch_facilities_by_type(self,facility_type: FacilityData, state_id: int, district_id: int, mht_id: int, health_block_id: int, portalCredentials: PortalCredentials) -> list[str]:
        """
        Just return the names list of each facility type
        """
        request_body = FacilityNameRequest(masterType=self.masterType_for_fetching_facility_names, stateID=state_id, districtID=district_id, healthBlockID=health_block_id, mhtid=mht_id, facilityType=facility_type.code)

        response = requests.post(url=self.facility_fetching_url,json=asdict(request_body),verify=False,headers=self._make_headers(credentials=portalCredentials))

        if response.status_code != 200:
            return []
        response_data = response.json()
        if not response_data["data"]:
            return []
        
        # print("-------------------------")
        # print(f"got response data for facility type : {facility_type.name} as: \n{response_data}")

        return [item["name"] for item in response_data["data"]]


    def _handle_catalog_creation(self,message:Message):
        # portalCredentials = PortalCredentials(acecss_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJMQUxCQVJSQS1SMSIsImp0aSI6IjdiZjAwMDk0ZDIzZDQ2Nzk5N2Y1ODc2ODZmNjIzMmQwIiwiaWF0IjoiMTc4Mzc0NDMzOCIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiNjA2NSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiOiJEUiBUUkFQVEkgUEFUSEFLIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiOCIsIkxvZ2luSUQiOiIxMjM2MDY1IiwiUm9sZU5hbWUiOiJNSFQgVXNlciIsIm5iZiI6MTc4Mzc0NDMzOCwiZXhwIjoxNzgzNzU1MTM4LCJpc3MiOiJyYnNrLWF1dGgiLCJhdWQiOiJyYnNrLWFwaSJ9.qGeXa-QGAcHSRMkQMd5JouNpVxq6EMB8lMLGSRrEwxI")
        registrationMetadata : UserRegistrationMetadata = message.payload["registrationMetadata"]
        portalCredentials: PortalCredentials = message.payload["portalCredentials"]

        # print(
        #     f"In facility worker, got portal credential as {message.payload['portalCredentials']}, "
        #     f"and type is {type(message.payload['portalCredentials'])}"
        # )
        # print("handle facility is called")
        facilities_by_type = {}
        all_facility_types = self._fetch_all_facility_type(stateId=registrationMetadata.state_id,portalCredentials=portalCredentials)
        # print(f"Got facility list as : {all_facility_types}")
        if not all_facility_types or len(all_facility_types) == 0:
            self._emit_event(event=Events.FETCHING_FACILITY_FAILED)
            return
   
        for facility_type in all_facility_types:
            all_facilities_of_a_type = self._fetch_facilities_by_type(facility_type=facility_type, state_id=registrationMetadata.state_id, district_id=registrationMetadata.district_id, mht_id=registrationMetadata.mht_code, health_block_id=registrationMetadata.health_block_id,portalCredentials=portalCredentials)
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