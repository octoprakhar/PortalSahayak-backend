from playwright.sync_api import sync_playwright

from workflow.workflow import ScreeningWorkflow

# main.py

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    page.locator('[title="Screening"]').click()
    page.wait_for_timeout(5000)
    page.locator('[name="financialMonth"]').select_option(label="May 2026")
    page.get_by_role('button',name='Search').click()
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(5000)
    input("Select the institution you want to fill students and then click enter....")
    
    #Adding new child now
    screeningWorkflow = ScreeningWorkflow(page=page)
    screeningWorkflow.run("./students_data_naitra2.csv","6263656106","Naitra")


    input("Press enter to close")
    print(page.title())
    browser.close()

# LALBARRA-R1
# Trapti@1234