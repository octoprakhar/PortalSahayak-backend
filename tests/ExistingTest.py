from playwright.sync_api import sync_playwright
import logging

from constants.log_type import LogType
from disease.factory.DiseaseCountFactory import DiseaseCountFactory
from all_models.ClassRange import ClassRange

from services.PageSynchronizer import PageSynchronizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

from all_models.child_models import Child
from workflow.ExistingChildrenWithoutData import ExistingChildrenWithoutData

child = Child(
    name="ansh",
    dob="16-08-2020",
    fatherName="Akash",
    motherName="Amrita",
    mobileNumber="999999999",
    gender="M",
    address="a",
    height="23",
    weight="2"
)

selected_mapping = {
        "District Level Facility": "DIST HOSPITAL BALAGHAT (District Level Facility)",
        "Block Level Facility": "CHC LALBARRA (Block Level Facility)",
        "NRC": "NRC DH BALAGHAT (NRC)",
        "DEIC": "DEIC Balaghat (DEIC)"
    }

def logger(msg:str,logType: LogType) -> None:
    pass


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    page.locator('[title="Screening"]').click()
    page.wait_for_load_state("networkidle")
    page.locator('[name="financialMonth"]').select_option(label="May 2026")
    page.get_by_role('button',name='Search').click()
    page.wait_for_load_state('networkidle')
    input("Select the institution you want to fill students and then click enter....")
    
    factory = DiseaseCountFactory()
    count_manager = factory.create(1)
    existingChildren = ExistingChildrenWithoutData(mobileNumber="6265449307", address="GARAPURI", page=page,count_manager=count_manager, selected_mapping=selected_mapping, max_children_count=0, institution_type="school", class_range=ClassRange(from_class=9, to_class=9), job_id="ABC",synchronizer=PageSynchronizer())
    existingChildren.addExistingChildren()
    page.wait_for_timeout(3000)
