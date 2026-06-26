from playwright.sync_api import sync_playwright

from services.ExistingChildScanner import ExistingChildScanner

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")

    child_scanner = ExistingChildScanner(page=page)
    child_scanner.get_total_existing_student()
    page.wait_for_timeout(5000)