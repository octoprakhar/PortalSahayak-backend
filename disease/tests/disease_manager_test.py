from playwright.sync_api import sync_playwright

from disease.manager.DiseaseManager import DiseaseManager
from all_models.child_models import Child
from services.PageSynchronizer import PageSynchronizer

from disease.manager.DiseaseCountManager import DiseaseCountManager

child = Child(
    name="A",
    dob="16-10-2023",
    facilityName="B",
    motherName="c",
    mobileNumber="9999999999",
    gender="Male",
    address="xyz",
    height="70.5",
    weight="5.4",
    diseaseName="PSD",
    hb="10",
    headCircumference="47",
    fatherName="None",
    facilityType="None",
    visionLeft="6/6",
    visionRight="6/6"
)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    disease_manager = DiseaseManager(page=page,synchronizer=PageSynchronizer(),count_manager=DiseaseCountManager())
    page.wait_for_timeout(5000)
    disease_manager.manage(child=child)
    page.wait_for_timeout(5000)