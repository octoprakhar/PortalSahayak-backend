from playwright.sync_api import sync_playwright

from workflow.workflow import ScreeningWorkflow

# main.py

import logging

from workflow.InstitutionSelectionPage import InstitutionSelectionPage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from datetime import datetime
import random

def random_past_date_current_month_iso() -> str:
    today = datetime.now()

    # If today is the 1st, return today
    if today.day == 1:
        return today.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ).isoformat()

    random_day = random.randint(1, today.day - 1)

    random_date = today.replace(
        day=random_day,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    return random_date.isoformat()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    page.locator('[title="Screening"]').click()
    page.wait_for_timeout(5000)
    institutionSelection = InstitutionSelectionPage(date=random_past_date_current_month_iso(),page=page)
    required_institutions = institutionSelection.get_month_data()
    print(required_institutions)
    page.wait_for_timeout(2000)