from playwright.sync_api import sync_playwright
import logging

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
    

    existingChildren = ExistingChildrenWithoutData(mobileNumber="8120954660", address="LAVADA", page=page)
    existingChildren.addExistingChildren()
    page.wait_for_timeout(3000)
