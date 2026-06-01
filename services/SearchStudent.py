from playwright.sync_api import Page
import logging

from all_models.child_models import Child
from all_models.SearchStudentModels import SearchResult, SearchedStudentCandidate

class SearchStudent:
    def __init__(self, page:Page, child:Child):
        self.page = page
        self.child = child

    def _get_first_name(self)->str:
        """
        Returns the first name of the child, by striping and then return first part of string
        """
        full_name = self.child.name.strip()

        if not full_name:
            raise ValueError("Child name is empty")

        return full_name.split()[0].lower()
    

    def _fill_first_name(self, name:str):
        """
        Using locator fill that first name of the child, all small case.
        It returns nothing as it will do the playwright UI part.
        """
        searchInputField = self.page.locator('input[placeholder="Search..."]')
        searchInputField.fill(name)
        pass

    def _get_resulted_rows(self) -> list[SearchedStudentCandidate]:
        """
        After searching there will be some rows will come return them whole in list.
        Returns an object:
        name: string
        dob: string
        fatherName: string
        motherName: string
        isStartEditingPresent: bool
        """

        rows = self.page.locator("tbody tr").all()

        logging.info(f"Found rows: {len(rows)}")
        finalRows = []

        if rows:

            for row in rows:

                tds = row.locator("td")

                td_count = tds.count()

                # logging.info(f"TD count: {td_count}")

                if td_count >= 3:
                    try:
                        name = tds.nth(2).inner_text()
                        dob = tds.nth(4).inner_text()
                        fatherName = tds.nth(6).inner_text()
                        motherName = tds.nth(7).inner_text()

                        td12 = tds.nth(11)
                        firstElement = td12.locator("div > *").first
                        title = firstElement.get_attribute("title")

                        if title == "Start Screening":
                            isStartScreeningPresent = True
                        else:
                            isStartScreeningPresent = False
                        
                        finalRows.append(SearchedStudentCandidate(
                            name=name,
                            dob=dob,
                            fatherName=fatherName,
                            motherName=motherName,
                            isChildEligibleForScreening=isStartScreeningPresent,
                            locator=row
                        ))
                        
                    except Exception as e:
                        logging.exception(f"exception occured while getting rows: {e}")
                        continue

                    

                else:

                    logging.error(
                        "Row has less than 3 td"
                    )

        else:

            return []
        
        return finalRows


    def _normalize_dob(self,dob:str)-> str:
        """
        Changes string of DOB in dd-mm-yyyy
        """
        dob_parts = dob.strip().split('-')[::-1]
        return "-".join(dob_parts)

    def _filter_by_dob(self, studentList: list[SearchedStudentCandidate]) -> list[SearchedStudentCandidate]:
        """
        Take the list of all the students, then 
        1. Modify both dob to be of same type dd-mm-yyyy
        2. Match it for all students
        3. Return all the found matches
        """
        dob_eligible = []

        for student in studentList:
            if self._normalize_dob(student.dob) == self.child.dob:
                logging.info(f"🎉🎉🎉 Child Name : {student.name}, match the dob ; {student.dob} with desired dob : {self.child.dob}")

                dob_eligible.append(student)
            else:
                logging.info(f"Child Name : {student.name}, doesn't match the dob ; {student.dob} with desired dob : {self.child.dob}")
        
        return dob_eligible

    def _find_eligible_candidate(self, studentList: list[SearchedStudentCandidate]) -> SearchedStudentCandidate | None:
        """
        Just return the first candidate who has isStartScreening present will be eligible candate
        """

        for student in studentList:
            if student.isChildEligibleForScreening:
                return student
        
        return None



        

    def search(self) -> SearchResult | None:
        """
        It will search for student and then return the index of the student.
        Student can be found with: 
        If first name of student matched + DOB matched 
        """

        ## Steps to search
        ## Step 1: fill first name in search box
        childFirstName:str = self._get_first_name()
        self._fill_first_name(childFirstName)

        self.page.wait_for_timeout(1500)
        
        ## Step 2: Get the whole table from below
        resultedRows:list[SearchedStudentCandidate] = self._get_resulted_rows()
        if not resultedRows:
            # No result found
            return SearchResult(
                found=False,
                eligible=False
            )

        # logging.info(f"Got row data as :")
        # for row in resultedRows:
        #     logging.info(row)
        #     logging.info("----------------------------")


        ## Step 3: Narrow down more with checking DOB, the first student whose DOB matches enter it.
        matchedDobResults: list[SearchedStudentCandidate] = self._filter_by_dob(resultedRows)

        if not matchedDobResults:
            ## No result for search is found
            return SearchResult(
                found = False,
                eligible = False
            )
        

        ## Step 4: Then check when "Start Screening" button is present, if not then that student is already done and return -1 as index, if present, then return the index
        foundStudent: SearchedStudentCandidate = self._find_eligible_candidate(matchedDobResults)

        
        if foundStudent is None:
            ## It means student was there, but not "isStartScreening" type button is present. All were already entered
            return SearchResult(
                found=True,
                eligible=False
            )
        
        
        return SearchResult(
            found=True,
            locator=foundStudent.locator,
            eligible=True
        )
