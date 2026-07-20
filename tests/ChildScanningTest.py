from playwright.sync_api import sync_playwright
import logging

from services.ExistingChildScanner import ExistingChildScanner
from all_models.ClassRange import ClassRange



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    page.wait_for_timeout(5000)

    child_scanner = ExistingChildScanner(page=page, class_range=ClassRange(from_class=9, to_class=9), is_awc_screening=False)
    child_length = child_scanner.get_total_existing_student()
    logging.info(f"Total child length: {child_length}")
    page.wait_for_timeout(5000)