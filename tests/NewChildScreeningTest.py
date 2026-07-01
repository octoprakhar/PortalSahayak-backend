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
    name="Bhavya",
    dob="21-05-2022",
    fatherName="Lokesh",
    motherName="Lalita",
    gender="Female",
    weight="8",
    height="60",
    mobileNumber="9999999999",
    headCircumference="40",
    facilityName="DEIC Balaghat (DEIC)",
    facilityType="DEIC",
    hb="13",
    address="ABCD",
    diseaseName="Squint",
    visionLeft="6/6",
    visionRight="6/6"
)

def logger(msg:str,logType: LogType) -> None:
    pass

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    factory = DiseaseCountFactory()
    count_manager = factory.create(10)
    screeningPage = ChildScreeningPage(page=page,child=child, count_manager=count_manager,job_id="ABC",logger=logger, synchronizer=PageSynchronizer())
    screeningPage.submit()
    page.wait_for_timeout(5000)