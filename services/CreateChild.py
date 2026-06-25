import random
import math

from all_models.child_models import Child
from all_models.ExistingStudentModel import ExistingChildResult
from utils.loaderUtils import get_age,get_head_circumference,get_corrected_values


class ChildFactory:
    """
    This class creates all the health details of the child, if that child is not in database, and we wanna enter it. 
    It will take ExistingChild's basic detail, and give you the final child.
    """
    def __init__(self,child:ExistingChildResult,defaultContactNumber:str,address:str):
        self.existingChild = child
        self.defaultContactNumber = defaultContactNumber
        self.address = address

    def _normalizeDob(self,dob:str):
        """
        Changes age from yyyy-mm-dd to dd-mm-yyyy
        """
        dob_parts = dob.strip().split("-")[::-1]
        return "-".join(dob_parts)

    def _getHeightAndWeight(self) -> tuple[int,int]:
        """
        It creates normal height and weight of the child with respect to it's DOB
        """
        return get_corrected_values(math.floor(get_age(self.existingChild.dob)))

    def _createHb(self) -> int:
        """
        It gives hb in range of 10 to 14
        """
        return round(random.uniform(10, 14), 1) 

    def _getFacilityTypeAndName(self) -> tuple[str,str]:
        """
        This function gives the facility type and Facility Name, for Now it will just return 
        Facility Type : Block Level Facility,
        Facility Name: CHC LALBARRA (Block Level Facility)
        """
        return "Block Level Facility","CHC LALBARRA (Block Level Facility)"

    def _getHeadCircumference(self) -> int:
        """
        This function returns the headCircumference of the child based on his age to make it normal
        * 0-1 : 43
        * 1-2 : 46
        * 2-3 : 48
        * 3+ : 50
        """
        return get_head_circumference(get_age(self.existingChild.dob))


    def createChild(self)->Child:
        """
        Returns each child in format of 'Child' by creating all health details from height, weight, hb, disease, etc.
        """
        weight,height = self._getHeightAndWeight()
        hb = self._createHb()
        headCircumference = self._getHeadCircumference()
        facilityType,facilityName = self._getFacilityTypeAndName()
        return Child(
            name=self.existingChild.name,
            dob=self.existingChild.dob,
            fatherName=self.existingChild.fatherName,
            motherName=self.existingChild.motherName,
            mobileNumber= self.defaultContactNumber,
            gender=self.existingChild.gender,
            address=self.address,
            height=str(height),
            weight=str(weight),
            diseaseName= "",## Updated Now diseases will be assigned only by the diseaseManager for all the children
            hb=str(hb),
            headCircumference=str(headCircumference),
            facilityType=facilityType,
            facilityName=facilityName,
            visionLeft="6/6",
            visionRight="6/6"

        )
