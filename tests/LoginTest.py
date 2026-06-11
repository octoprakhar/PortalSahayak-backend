from playwright.sync_api import sync_playwright
import logging

from workflow.LoginPage import LoginPage
from all_models.FeedbackResult import FeedbackResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

url = "https://rbsk.mohfw.gov.in/RBSK/login"
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()

    page.goto(url)
    page.wait_for_timeout(1000)
    screening = page.locator('[title="Screening"]')
    loginPage = LoginPage(page=page,success_locator=screening)
    result : FeedbackResult = loginPage.login("LALBARRA-R1","Trapti@1234")

    print(result)


    page.wait_for_timeout(5000)