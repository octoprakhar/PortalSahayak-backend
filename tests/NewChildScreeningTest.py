from playwright.sync_api import sync_playwright
import logging

from all_models.child_models import Child
from workflow.ScreeningPage import ChildScreeningPage

from disease.manager.DiseaseCountManager import DiseaseCountManager
from constants.log_type import LogType
from services.PageSynchronizer import PageSynchronizer
from disease.factory.DiseaseCountFactory import DiseaseCountFactory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

child = Child(
    name="lamine yamal",
    dob="21-05-2017",
    fatherName="Lokesh",
    motherName="Lalita",
    gender="Male",
    weight="10.2",
    height="95",
    mobileNumber="9999999999",
    headCircumference="40",
    facilityName="DEIC Balaghat (DEIC)",
    facilityType="DEIC",
    hb="13",
    address="ABCD",
    diseaseName="Squint",
    visionLeft="6/6",
    visionRight="6/6",
    childClass=6,
    bloodPressure="100/70"
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
    factory = DiseaseCountFactory()
    count_manager = factory.create(1)
    screeningPage = ChildScreeningPage(page=page,child=child,institution_type="school", selected_mapping=selected_mapping, count_manager=count_manager,job_id="ABC",logger=logger, synchronizer=PageSynchronizer())
    screeningPage.submit()
    page.wait_for_timeout(5000)